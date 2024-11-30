from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from app.services.firebase import verify_firebase_token, upload_to_firebase, update_user_images
from app.services.model import predict_mask, preprocess_image
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import time

router = APIRouter()

# Configure logger
logging.basicConfig(level=logging.INFO)

@router.post("/predict")
async def predict(
    user_id: str = Form(...),
    firebase_token: str = Form(...),
    image: UploadFile = File(...),
    verified_user: dict = Depends(verify_firebase_token)
):
    """
    Handle the prediction request: Upload image and mask to Firebase Storage, make a prediction, 
    return the result, and store the image URLs in Firestore.
    """
    try:
        # Log the received values
        logging.info(f"Received user_id: {user_id}")
        logging.info(f"Verified user: {verified_user}")  # Log the decoded token information

        # Validate file type
        if not image.filename.lower().endswith((".jpg", ".jpeg")):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPG or JPEG image.")

        # Read and validate image data
        image_data = await image.read()
        try:
            input_image = Image.open(BytesIO(image_data))
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="Invalid image file. Could not process the uploaded image.")

        # Generate a unique filename based on user_id and current time
        timestamp = int(time.time())
        base_name = f"{user_id}_{timestamp}"

        # Upload the original image to Firebase
        original_image_url = upload_to_firebase("procare-images/image", f"{base_name}_original.jpg", image_data, "image/jpeg")

        # Preprocess the image and make a prediction
        preprocessed_image = preprocess_image(input_image)
        predicted_mask = predict_mask(preprocessed_image)

        # Convert the prediction to an image
        mask_image = Image.fromarray((predicted_mask * 255).astype("uint8"))  # Convert to grayscale image

        # Save the mask to a BytesIO buffer
        mask_byte_arr = BytesIO()
        mask_image.save(mask_byte_arr, format="JPEG")
        mask_byte_arr.seek(0)

        # Upload the mask image to Firebase
        mask_image_url = upload_to_firebase("procare-images/mask", f"{base_name}_mask.jpg", mask_byte_arr.getvalue(), "image/jpeg")

        # Update the Firestore document with the image URLs
        update_user_images(user_id, original_image_url, mask_image_url)

        # Return the response with image and mask URLs
        return JSONResponse(
            content={
                "message": "Prediction successful",
                "original_image_url": original_image_url,
                "mask_image_url": mask_image_url,
            }
        )

    except HTTPException as http_ex:
        logging.error(http_ex)
        raise http_ex
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
