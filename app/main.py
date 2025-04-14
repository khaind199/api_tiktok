from fastapi import FastAPI
from .models import ReviewRequest
from .services import get_tiktok_reviews

app = FastAPI()

@app.post("/tiktok_reviews")
def get_reviews(data: ReviewRequest):
    result = get_tiktok_reviews(data)
    return result
