from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image

router = APIRouter()

@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    """
    Handle the prediction request: Accepts a JPG MRI image file and returns a JPG mask image.
    """
    try:
        # Read the image file
        image_data = await image.read()  # Read the uploaded file content
        input_image = Image.open(BytesIO(image_data))  # Open the image (ensure it is JPG)

        # TODO: Replace mock code with actual model logic
        # For now, we just return the same input image as the mask

        # Save the input image into a BytesIO buffer as JPG
        img_byte_arr = BytesIO()
        input_image.save(img_byte_arr, format='JPEG')  # Save the input image as JPG
        img_byte_arr.seek(0)  # Reset pointer to the beginning of the buffer

        # Return the same image as the "mask" in the response
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
