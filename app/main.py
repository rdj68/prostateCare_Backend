from fastapi import FastAPI
from app.routes import prediction

# Initialize the FastAPI app
app = FastAPI()

# Include the prediction route
app.include_router(prediction.router)

# Home route (optional)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI prediction service!"}
