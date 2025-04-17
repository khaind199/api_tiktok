from fastapi import FastAPI, Query
from .models import ReviewTikTokRequest, ReviewShopeRequest, RecommendTikTokRequest
from .services import get_tiktok_reviews, get_shopee_reviews, get_sold_tiktok, get_tiktok_search, get_tiktok_product, get_tiktok_recommend
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/tiktok_reviews")
def get_reviews(data: ReviewTikTokRequest):
    try:
        result = get_tiktok_reviews(data)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/shopee_reviews")
def fetch_reviews(
    shop_id: int = Query(..., description="Shop ID trên Shopee"),
    limit: int = Query(6, ge=1, le=100, description="Số review muốn lấy"),
    offset: int = Query(0, ge=0, description="Offset để phân trang"),
):
    try:
        return get_shopee_reviews(shop_id=shop_id, limit=limit, offset=offset)
    except Exception as e:
            return {"error": str(e)}
        
@app.get("/sold_tiktok")
def fetch_reviews(
    product_id: int = Query(..., description="product ID")
):
    try:
        data = get_sold_tiktok(product_id)
        return JSONResponse(content=data)
    except Exception as e:
       return {"error": str(e)}
   
   
@app.post("/tiktok_search")
def get_reviews():
    try:
        result = get_tiktok_search()
        return result
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/tiktok_product")
def get_reviews():
    try:
        result = get_tiktok_product()
        return result
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/recommend")
def get_reviews(data: RecommendTikTokRequest):
    try:
        result = get_tiktok_recommend(data)
        return result
    except Exception as e:
        return {"error": str(e)}