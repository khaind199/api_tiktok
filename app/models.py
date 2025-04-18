from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel


class ReviewTikTokRequest(BaseModel):
    product_id: str
    seller_id: str
    cursor: int = 0
    
# class ReviewShopeRequest(BaseModel):
#     shop_id: int
#     limit: Optional[int] = 6
#     offset: Optional[int] = 0
    
class SoldTikTokRequest(BaseModel):
    product_id: str
    
class ProductTikTokRequest(BaseModel):
    next_scroll_param: int
    
class RecommendTikTokRequest(BaseModel):
    product_id: str
    cursor: int
    author_id: str
    seller_id: str
    
class SearchTikTokRequest(BaseModel):
    keyword: str
    offset: Optional[int] = 0
    count: Optional[int] = 10