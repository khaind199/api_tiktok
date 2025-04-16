import requests
import time

def get_all_reviews(shop_id, item_id=None, limit=6):
    all_reviews = []
    offset = 0

    while True:
        url = "https://shopee.vn/api/v4/item/get_ratings"
        params = {
            "filter": 0,
            "flag": 1,
            "limit": limit,
            "offset": offset,
            "shopid": shop_id,
            "itemid": item_id or 0,  # Nếu không có item_id thì set = 0
            "type": 0
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://shopee.vn/product/{shop_id}/{item_id or ''}"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            print(f"📦 Offset: {offset}, Trạng thái: {data.get('error_msg')}")

            items = data.get("data", {}).get("items", [])
            if not items:
                print("✅ Đã lấy hết đánh giá.")
                break

            all_reviews.extend(items)
            offset += limit
            time.sleep(1)  # Tránh bị block

        except Exception as e:
            print(f"❌ Lỗi khi lấy review: {e}")
            break

    return all_reviews


# --- Chạy thử ---
if __name__ == "__main__":
    shop_id = 1227186803
    item_id = 24272630146
    reviews = get_all_reviews(shop_id, item_id)
    print(f"📊 Số lượng đánh giá lấy được: {len(reviews)}")

    # In thử vài review
    for r in reviews[:3]:
        print(f"- {r['author_username']}: {r['comment']}")
