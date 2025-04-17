import requests
import random
from .config import API_URL, DEVICE_ID, AID, LOCALE, TIKTOK_COOKIE, SHOPEE_COOKIE, SOLD_TIKTOK_COOKIE
from .models import ReviewTikTokRequest, ReviewShopeRequest, RecommendTikTokRequest
from typing import Optional, List
from datetime import datetime
import time
from bs4 import BeautifulSoup
import json

PROXY_LIST = [
    # "http://14.230.122.197:49372",
    # "http://116.103.79.120:50393",
] # my proxy

proxy_index = 0

def format_timestamp(ts_ms):
    try:
        ts = int(ts_ms) / 1000
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Invalid timestamp"

def to_time_ago(timestamp):
    now = int(time.time())  # thời gian hiện tại (epoch)
    ts = int(timestamp)
    diff = now - ts

    if diff < 60:
        return f"{diff} seconds ago"
    elif diff < 3600:
        return f"{diff // 60} minutes ago"
    elif diff < 86400:
        return f"{diff // 3600} hours ago"
    elif diff < 2592000:
        return f"{diff // 86400} days ago"
    elif diff < 31536000:
        return f"{diff // 2592000} months ago"
    else:
        return f"{diff // 31536000} years ago"

def get_tiktok_reviews(data: ReviewTikTokRequest):
    url = f"{API_URL}?device_id={DEVICE_ID}&aid={AID}&locale={LOCALE}"
    global proxy_index
    
    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': TIKTOK_COOKIE
    }
    
    
    payload = (
        '{\n'
        '  "product_id": "' + data.product_id + '",\n'
        '  "seller_id": "' + data.seller_id + '",\n'
        '  "need_filter": false,\n'
        '  "size": 10,\n'
        '  "cursor": ' + str(data.cursor) + ',\n'
        '  "traffic_source_list": [6],\n'
        '  "need_count": true,\n'
        '  "sort_type": 2\n'
        '}'
    )
    
    response = requests.post(url, headers=headers, data=payload, proxies=proxies)
    res_json = response.json()

    reviews = []
    for item in res_json.get("data", {}).get("review_items", []):
        parent_item = item.get("review_item", {})
        product_card = item.get("product_card", {})
        review_data = parent_item.get("review", {})
        user_data = parent_item.get("review_user", {})
        image_urls = product_card.get("display_image", {}).get("url_list", [])
        
        review = {
            "review_id": review_data.get("review_id"),
            "rating": review_data.get("rating"),
            "text": review_data.get("display_text", "").strip(),
            "timestamp": format_timestamp(review_data.get("review_timestamp")),
            "time_ago": review_data.get("review_timestamp_fmt").strip(),
            "user_name": user_data.get("name"),
            "user_id": user_data.get("user_id"),
            "sku_id": parent_item.get("sku_id"),
            "sku": parent_item.get("sku_specification"),
            "review_user": parent_item.get("review_user"),
            "product_name": product_card.get("display_product_name"),
            "product_image": image_urls[0] if image_urls else None,
            "price": {
                "original": product_card.get("display_origin_price"),
                "real": product_card.get("display_real_price"),
            }
        }
        reviews.append(review)

    return {
        "reviews": reviews,
        "has_more": res_json.get("data", {}).get("has_more", False),
        "next_cursor": res_json.get("data", {}).get("next_cursor", 0),
        "top_text": res_json.get("data", {}).get("top_text", ""),
        "review_count": res_json.get("data", {}).get("review_count", 0)
    }

def get_shopee_reviews(shop_id: int, limit: int = 6, offset: int = 0) -> dict:
    url = f"https://shopee.vn/api/v4/seller_operation/get_shop_ratings_new?limit={limit}&offset={offset}&shopid={shop_id}"

    global proxy_index
    
    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Cookie': SHOPEE_COOKIE
    }

    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
    response.raise_for_status()
    res_json = response.json()

    reviews = []
    for item in res_json.get("data", {}).get("items", []):
        product = item.get("product_items", [{}])[0]
        
        review = {
            "comment_id": item.get("cmtid"),
            "rating": item.get("rating_star") or item.get("rating"),
            "text": item.get("comment", "").strip(),
            "timestamp": item.get("ctime"),
            "time_ago": to_time_ago(item.get("ctime")) or None,
            "user_id": item.get("userid"),
            "user_name": item.get("author_username"),
            "avatar": (
                f"https://down-vn.img.susercontent.com/file/{item.get('author_portrait')}"
                if item.get("author_portrait") else None 
            ), 
            "product_name": product.get("name"),
            "model_name": product.get("model_name"),
            "product_image": (
                f"https://down-vn.img.susercontent.com/file/{product.get('image')}"
                if product.get("image") else None
            )
        }

        reviews.append(review)

    return reviews

def get_sold_tiktok(product_id: int) -> dict:
    url = f"https://www.tiktok.com/view/product/{product_id}"
    global proxy_index
    
    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Cookie': SOLD_TIKTOK_COOKIE
    }

    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", {"id": "__MODERN_ROUTER_DATA__"})
    if not script_tag:
        return {"error": "Script data not found"}

    try:
        data = json.loads(script_tag.string)
    except Exception:
        return {"error": "Failed to parse JSON"}

    loader_data = data.get("loaderData", {})
    initial_data = None
    for value in loader_data.values():
        if isinstance(value, dict) and "initialData" in value:
            initial_data = value["initialData"]
            break
    if not initial_data:
        return {"error": "initialData not found"}

    product_info = initial_data.get("productInfo", {})
    seller_info = product_info.get("seller", {})
    base = product_info.get("product_base", {})

    # Parse desc_detail nếu là string JSON
    desc = ""
    desc_detail_raw = base.get("desc_detail", "")
    if isinstance(desc_detail_raw, str):
        try:
            desc_list = json.loads(desc_detail_raw)
            desc = "\n".join(x["text"] for x in desc_list if x.get("type") == "text")
        except Exception:
            desc = "No Description"
    elif isinstance(desc_detail_raw, list):
        desc = "\n".join(x["text"] for x in desc_detail_raw if x.get("type") == "text")
    price_info = base.get("price", {})
    formatted_price = {
        "original_price": price_info.get("original_price", ""),
        "real_price": price_info.get("real_price", ""),
        "discount": price_info.get("discount", ""),
        "currency": price_info.get("currency", ""),
        "currency_symbol": price_info.get("currency_symbol", "")
    }

    return {
        "product_id": str(product_id),
        "title": base.get("title", "No Title"),
        "description": desc or "No Description",
        "thumbnail": base.get("images", [{}])[0].get("thumb_url_list", [""])[0],
        "specifications": base.get("specifications", ""),
        "sold_count": base.get("sold_count", ""),
        "price": formatted_price,
        "seller": {
            "id": seller_info.get("seller_id"),
            "name": seller_info.get("name"),
            "avatar": seller_info.get("avatar", {}).get("url_list", [""])[0],
            "location": seller_info.get("seller_location", ""),
            "link": seller_info.get("link", "")
        },
        "fetched_at": datetime.now().isoformat() 
        
    }


def get_tiktok_search():
    url = f"https://search19-normal-alisg.tiktokv.com/aweme/v1/general/search/single/?cursor=0&enter_from=homepage_hot&backtrace&count=10&last_search_id=202504160438055547AE55912B93969D9F&query_correct_type=1&is_filter_search=1&search_source=tab_search&search_id&enable_lite_workflow=1&sort_type=3&enable_lite_cut=1&publish_time=1&end_to_end_search_session_id=7703670413758991846&keyword=trend+n%E1%BB%ADa+qu%E1%BA%A7n&request_tag_from=h5&is_non_personalized_search=0&manifest_version_code=380602&_rticket=1744778297093&app_language=vi&app_type=normal&iid=7491245982002743047&app_package=com.zhiliaoapp.musically.go&channel=googleplay&device_type=SM-G988N&language=vi&host_abi=x86_64&locale=vi-VN&resolution=720*1280&openudid=dca1452e335c3eb8&update_version_code=380602&ac2=wifi5g&cdid=96a95da2-c1a4-40c7-b1f0-b07a5ce36f16&sys_region=VN&os_api=28&timezone_name=Asia%2FBangkok&dpi=240&carrier_region=VN&ac=wifi&device_id=6967523334011815425&os_version=9&timezone_offset=25200&version_code=380602&app_name=musically_go&ab_version=38.6.2&version_name=38.6.2&device_brand=samsung&op_region=VN&ssmix=a&device_platform=android&build_number=38.6.2&region=VN&aid=1340&ts=1744778255&ecom_version=350900&ecomAppVersion=35.9.0&ecom_version_code=350900&ecom_version_name=35.9.0&ecom_appid=614896&ecom_build_number=1.0.10-alpha.0&ecom_commit_id=af623b1cc&ecom_aar_version=1.0.10-alpha.0"

    global proxy_index
    
    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        "X-Argus": "QagPj9gVcKCZYeOWLGWYCmBhM/YuW41r5DHdjpYE9zthjdha/5otf9Zu4xK5WsMkT+7OemavxpSb4nPdXQq0be8hzXfULoMLGpcwHc0KQSmcYyw4F7v9r7pTlHA/hQuKdvd6p+3ijw73V60TzVpX1B+icsfLih9ykXVvhQj6KHJFp+QzGE6qu5/ZHCnX+i3M/7ClNJ54CprjixWhyLN1dp3EMkVy1DSg5p9Oa5tbcYi8wsH92L4Uxug74PoGMtVpThP9X1B0a8zdblIbOuDiUGaY8uv+8FREGR5p12c9j2rLPzHRp/CiQTx+RAhDulO+SMLF5ai/RoXCLXXZfQQhSifbjBplwsXcnHrJ2aGRrJExNOAOTucnRCXO2xpcXBqIgmyywWefdU0qX8AWuKbGJoO+RqYJvnaH/mt1SZJnEWpju7rU1M+1o/JQ6Az2DB3Cf7au+q5jvF2kj0YtKPco7toSS4iuL4b5kdTgY/Ddq0HI9/niVtO0fIxKEIUkaskNdDyJrtXa0eOsAhAjTM2EhUk7uJ0FOzenaqLkuxGqg4AQCWlYe65eJfr2VL+IZIzNQz+V3YO949E1fPFXYPeIKapPChNpAn6zx5QKV4onUMy1yQ==",
        "X-Ladon": "6/dVLdAOfkz0bk2eVxplSwo9UZvwa1+CLcBGAudkOWTwKutK",
        "x-tt-req-timeout": "90000",
        "Content-Type": "text/plain",
        "Cookie": "odin_tt=378ff5388b6314b2193d1a864137b3a8acf42f6c83f4ddbab572c15935ab52da1663da899a3c5def73f6402838f1c90a02afb5016a5970ee6f416919db71285e34c9be7d81d5ba08c6f1de8e772144e2",
    }
    
    payload = (
        '{\n'
        '  "kol_id":"MS4wLjABAAAAOMfhnMOS250cYxEal8wjpyRWEVaUWktVT2zKmBg9YFDiGN4qcuxyfGHqK-qwfRwd",\n'
        '  "count":10,\n'
        '  "next_scroll_param":"0",\n'
        '  "session_id":"1564401297040",\n'
        '  "enter_from":"click",\n'
        '  "exposed_product_id_list":[],\n'
        '  "use_kol_for_recommend":false,\n'
        '  "video_id":""\n'
        '  "video_product_id":[],\n'
        '  "protocol_version":2\n'
        '}'
    )

    response = requests.get(url, headers=headers, data=payload, proxies=proxies, timeout=10)
    response.raise_for_status()
    res_json = response.json()
    
    list_aweme_ids  = []
    for item in res_json.get("data", []):
        aweme_info = item.get("aweme_info",{})
        added_sound_music_info = aweme_info.get("added_sound_music_info", {})
        id = added_sound_music_info.get("id_str", "")
        if id is not None:
            list_aweme_ids.append(id)

    return {
        "list_aweme_infos": list_aweme_ids ,
        "has_more": res_json.get("has_more", ""),
        "cursor": res_json.get("cursor", 0),
    }


def get_tiktok_product():
    url = f"https://oec22-normal-alisg.tiktokv.com/api/showcase/v1/profile_tab_product/list?iid=7493053746571724599&device_id=7493023054664418871&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=280605&version_name=28.6.5&device_platform=android&ab_version=28.6.5&ssmix=a&device_type=SM-J730G&device_brand=samsung&language=en&os_api=28&os_version=9&openudid=3d4dc3e77ddcc9fb&manifest_version_code=2022806050&resolution=1080*1920&dpi=420&update_version_code=2022806050&_rticket=1744766425632&current_region=VN&app_type=normal&sys_region=US&mcc_mnc=45202&timezone_name=Asia%2FHo_Chi_Minh&carrier_region_v2=452&residence=VN&app_language=en&carrier_region=VN&ac2=wifi&uoo=0&op_region=VN&timezone_offset=25200&build_number=28.6.5&host_abi=armeabi-v7a&locale=en&region=US&ts=1744766426&cdid=e928b21d-15c8-458a-a5f1-8d93b0bc545d"

    global proxy_index
    
    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'com.zhiliaoapp.musically/2022806050(Linux;U;Android9;en;SM-J730G;Build/PPR1.180610.011;Cronet/TTNetVersion:d23bd1142023-01-13QuicVersion:5f23035d2022-11-23)',
        'Cookie': 'odin_tt=378ff5388b6314b2193d1a864137b3a8acf42f6c83f4ddbab572c15935ab52da1663da899a3c5def73f6402838f1c90a02afb5016a5970ee6f416919db71285e34c9be7d81d5ba08c6f1de8e772144e2'
    }

    payload = (
        '{\n'
        '  "kol_id":"MS4wLjABAAAAOMfhnMOS250cYxEal8wjpyRWEVaUWktVT2zKmBg9YFDiGN4qcuxyfGHqK-qwfRwd",\n'
        '  "count":10,\n'
        '  "session_id":"2716107296722",\n'
        '  "enter_from":"general_search",\n'
        '  "next_scroll_param":"3",\n'
        '  "exposed_product_id_list":[],\n'
        '  "search_card_live_product_id_list":[],\n'
        '  "search_card_no_live_product_id_list":[]\n'
        '}'
    )

    time.sleep(random.uniform(1.5, 4.5))
    response = requests.post(url, headers=headers, data=payload, proxies=proxies, timeout=10)
    response.raise_for_status()
        
    res_json = response.json()
        
    product_lists = []
    for item in res_json.get("data", {}).get("products", {}).get("product_list", []):
            product_list = {
                "product_id": item.get("product_id"),
                "product_name": item.get("product_name", ""),
                "product_sold_count": item.get("product_sold_count", ""),
                "format_origin_price": item.get("format_origin_price", ""),
                "format_available_price": item.get("format_available_price", ""),
                "discount": item.get("discount", ""),
                "display_sold_count": item.get("display_sold_count", ""),
                "sold_count_info": item.get("sold_count_info", ""),
            }
            product_lists.append(product_list)

    pagination_info = res_json.get("data", {}).get("products", {})
    return {
            "product_lists": product_lists,
            "has_more": pagination_info.get("has_more", ""),
            "next_scroll_param": pagination_info.get("next_scroll_param", 0),
        }
    
def get_tiktok_recommend(data: RecommendTikTokRequest):
    url = f"https://oec22-normal-alisg.tiktokv.com/api/v1/shop/recommend/same_shop/get?iid=7493820152778852151&device_id=7493023054664418871&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=280605&version_name=28.6.5&device_platform=android&ab_version=28.6.5&ssmix=a&device_type=SM-J730G&device_brand=samsung&language=en&os_api=28&os_version=9&openudid=3d4dc3e77ddcc9fb&manifest_version_code=2022806050&resolution=1080*1920&dpi=420&update_version_code=2022806050&_rticket=1744855420835&current_region=VN&app_type=normal&sys_region=US&mcc_mnc=45202&timezone_name=Asia%2FHo_Chi_Minh&carrier_region_v2=452&residence=VN&app_language=en&carrier_region=VN&ac2=wifi&uoo=0&op_region=VN&timezone_offset=25200&build_number=28.6.5&host_abi=armeabi-v7a&locale=en&region=US&ts=1744855419&cdid=a65772cf-f4d7-4ef0-9406-a27665c468d9"

    global proxy_index
    
    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'com.zhiliaoapp.musically/2022806050 (Linux; U; Android 9; en; SM-J730G; Build/PPR1.180610.011; Cronet/TTNetVersion:d23bd114 2023-01-13 QuicVersion:5f23035d 2022-11-23)',
        'Cookie': 'odin_tt=668bc7e986958a22e0bfed63eac2a0b15b8b0778a8d54f2c0477a0f9fb108bc46436c365d56021e4e9fcaae77bfc6f0481b955d7a808cd285fe195ccdced4474a7655b0c92e8a9721543cdceeddabd8a; install_id=7493820152778852151; ttreq=1$5e253034103781cac1ec95ba7012a3985dd24c09',
        'Host': 'oec22-normal-alisg.tiktokv.com'
    }

    payload = json.dumps({
        "product_id": data.product_id,
        "scene": "pdp_shop_recommend",
        "size": 6,
        "cursor": data.cursor,
        "first_source_page": "mall",
        "enter_from_info": "mall",
        "author_id": data.author_id,
        "seller_id": data.seller_id,
        "product_source_info": 6,
        "traffic_source_list": [6]
    })

    response = requests.post(url, headers=headers, data=payload, proxies=proxies, timeout=10)
    response.raise_for_status()
        
    res_json = response.json()
    
    product_lists = []
    for item in res_json.get("data", {}).get("feed_list", []):
            id =  item.get("id")
            if id is not None:
                product_lists.append(id)

    pagination_info = res_json.get("data", {})
    return {
            "product_lists": product_lists,
            "has_more": pagination_info.get("has_more", ""),
            "next_cursor": pagination_info.get("next_cursor", 0),
            "request_id": pagination_info.get("request_id", ""),
            "title": pagination_info.get("title", ""),
            
        }
