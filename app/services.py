import requests
import random
from .config import API_URL, DEVICE_ID, AID, LOCALE, TIKTOK_COOKIE, SHOPEE_COOKIE
from .models import ReviewTikTokRequest, ReviewShopeRequest
from typing import Optional, List

def get_tiktok_reviews(data: ReviewTikTokRequest):
    url = f"{API_URL}?device_id={DEVICE_ID}&aid={AID}&locale={LOCALE}"

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': TIKTOK_COOKIE
    }
    
    proxy = random.choice(data.proxies) if data.proxies else None

    proxies = {
        "http": proxy,
        "https": proxy
    } if proxy else None
    
    response = requests.post(url, headers=headers, json=data.dict(), proxies=proxies)
    return response.json()

def get_shopee_reviews(shop_id: int, limit: int = 6, offset: int = 0, proxies: Optional[List[str]] = None) -> dict:
    url = f"https://shopee.vn/api/v4/seller_operation/get_shop_ratings_new?limit={limit}&offset={offset}&shopid={shop_id}"

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Cookie': SHOPEE_COOKIE
    }
    proxy = random.choice(proxies) if proxies else None
    
    proxy_dict = {
        "http": proxy,
        "https": proxy
    } if proxy else None

    response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
    response.raise_for_status()
    return response.json()
