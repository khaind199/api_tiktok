from fastapi import FastAPI, Query
from .models import ReviewTikTokRequest, ReviewShopeRequest
from .services import get_tiktok_reviews, get_shopee_reviews
from typing import List, Optional

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
    proxy: Optional[str] = Query(default=None, description="Danh sách proxy. VD: ?proxies=http://ip1:port, proxies=http://ip2:port")
):
    try:
        proxy_list = proxy.split(",") if proxy else None
        return get_shopee_reviews(shop_id=shop_id, limit=limit, offset=offset, proxies=proxy_list)
    except Exception as e:
            return {"error": str(e)}