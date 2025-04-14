import requests
from .config import API_URL, DEVICE_ID, AID, LOCALE, COOKIE
from .models import ReviewRequest

def get_tiktok_reviews(data: ReviewRequest):
    url = f"{API_URL}?device_id={DEVICE_ID}&aid={AID}&locale={LOCALE}"

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': COOKIE
    }

    # Truyền dữ liệu dưới dạng JSON vào trong body request
    response = requests.post(url, headers=headers, json=data.dict())
    return response.json()
