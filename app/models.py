from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel


class ReviewTikTokRequest(BaseModel):
    product_id: str
    seller_id: str
    need_filter: bool = True
    size: int = 10
    cursor: int = 1
    kol_id: str
    traffic_source_list: List[int] = [6]  
    need_count: bool = True
    proxies: Optional[List[str]] = None


class ReviewShopeRequest(BaseModel):
    shop_id: int
    limit: Optional[int] = 6
    offset: Optional[int] = 0
    