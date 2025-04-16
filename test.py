import requests
import json

url = "https://oec16-normal-alisg.tiktokv.com/api/v1/shop_review/list?device_id=7493023054664418871&aid=1233&locale=en"

headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'Cookie': 'store-idc=alisg; store-country-code=vn; store-country-code-src=did; store-country-sign=MEIEDE5phQnH_TpACEdrsgQgyvgepS6eQYM9PTlGdTHCJoLBqpZU4AUjvY3YjUYTM0sEEJbkqaYUBEmwvwIwLR1cWtI; install_id=7493053746571724599; ttreq=1$6a9e36036d4792683498299f1f5f8e0d821aeef1; tt-target-idc=alisg; odin_tt=81f657b81cd32c53ebaafd3d72951ca6eef6c3e3a3e46bdf62f72bc8afe1fe1d867af0676cbcfab8f7bacc7ad43d2886a47a712ceac7a15f163f60e05d1f396a2eb5a44080f47d44ad5cd59efee52fe9; passport_csrf_token=47d76998f251b9e12ef9da54648a47d1; passport_csrf_token_default=47d76998f251b9e12ef9da54648a47d1; msToken=ypatvIdutHry_Ukh5pysH1jCu1iKJ2veEgjT9Bl7G57pM9PBti8eG-I-a3wnh3IHQygVmIstkEp1MHp0DQYYYHzQ0rvweIVnEFkpxoqOZ5o=; odin_tt=378ff5388b6314b2193d1a864137b3a8acf42f6c83f4ddbab572c15935ab52da1663da899a3c5def73f6402838f1c90a02afb5016a5970ee6f416919db71285e34c9be7d81d5ba08c6f1de8e772144e2',
    'User-Agent': 'com.zhiliaoapp.musically/2022806050 (Linux; U; Android 9; en; SM-J730G; Build/PPR1.180610.011; Cronet/TTNetVersion:d23bd114 2023-01-13 QuicVersion:5f23035d 2022-11-23)'
}

payload_template = {
    "product_id": "1732176716973246924",
    "seller_id": "7495372109224708556",
    "need_filter": True,
    "size": 10,
    "cursor": 1,
    "kol_id": "6825358298771948546",
    "traffic_source_list": [6],
    "need_count": True
}

def get_reviews(cursor):
    payload = payload_template.copy()
    payload["cursor"] = cursor
    response = requests.post(url, headers=headers, json=payload)
    try:
        return response.json()
    except json.JSONDecodeError:
        print("❌ Response không phải JSON hợp lệ.")
        return {}

# Start fetching pages
cursor = 1
page = 1

while True:
    print(f"\n🔹 Page {page} - Cursor: {cursor}")
    response_data = get_reviews(cursor)

    if "data" not in response_data:
        print("❌ Không có dữ liệu. Dừng lại.")
        break

    data = response_data["data"]
    reviews = data.get("review_items", [])
    print(f"✅ Số review trong trang này: {len(reviews)}")

    if not data.get("has_more", False):
        print("🚫 Hết dữ liệu (has_more = false). Dừng.")
        break

    next_cursor = data.get("next_cursor")
    if not next_cursor:
        print("⚠️ Không có next_cursor. Dừng.")
        break

    cursor = next_cursor
    page += 1
