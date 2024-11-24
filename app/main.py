from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import prediction

app = FastAPI()

origins = [
    "*",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

app.include_router(prediction.router)

# Home route (optional)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI prediction service!"}
