import requests
import random
from .config import API_URL, DEVICE_ID, AID, LOCALE, TIKTOK_COOKIE, SHOPEE_COOKIE, SOLD_TIKTOK_COOKIE
from .models import ReviewTikTokRequest, RecommendTikTokRequest, SearchTikTokRequest
from typing import Optional, List
from datetime import datetime
import time
from bs4 import BeautifulSoup
import json
from urllib.parse import quote

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

def get_tiktok_search(data: SearchTikTokRequest):
    global proxy_index

    random_did = random.randint(1241242141211411412, 7465151651135121111)

    url = (
        "https://search22-normal-c-alisg.tiktokv.com/aweme/v1/search/item/"
        f"?device_platform=android"
        f"&channel=googleplay"
        f"&aid=1180"
        f"&app_name=trill"
        f"&version_code=390505"
        f"&device_type=SM-N976N"
        f"&device_brand=samsung"
        f"&os_version=12"
        f"&device_id={random_did}"
    )

    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1 

    proxies = {"http": proxy, "https": proxy} if proxy else None
    encoded_keyword = quote(data.keyword)

    payload = (
        f"keyword={encoded_keyword}"
        f"&offset={data.offset}"
        f"&count={data.count}"
        f"&source=video_search"
        f"&query_correct_type=1"
        f"&is_filter_search=1"
        f"&sort_type=3"
    )

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'install_id=7495601926983091989; ttreq=1$67956dd627f467ba7da5628ee610d91d3f5c0c4a; odin_tt=142852b59cb99122e16b294481b0c2409e1a2950ef0805ac84ca2659d42ce68be947f2a0667101ea0699f1d646667c47439dcad1b9141c42c74bffa2e7084b16563bfa79392313131d380efa2f81b6a4; store-idc=alisg; store-country-sign=MEIEDMEKk3457CFs-VDpggQg46Yup5ACIzPYnSz9zKhfP9CnQgLVSthii7aXMagh2hoEEEqCnaJ9V4NtDTd2y7LKnPw; store-country-code=kr; store-country-code-src=did; odin_tt=c97fd3f6f83affd582dba1966c4edca011b6686083ab86123f7cef8738687807d6a785a71b76c4544d522a0e812f68891da82d6500634f41bfdb512195f9dacced1ceb7033b1090853d8054023688ebf',
        'User-Agent': 'com.ss.android.ugc.trill/390505 (Linux; U; Android 12; vi_VN; SM-N976N; Build/QP1A.190711.020;tt-ok/3.12.13.17)',
        'X-Ladon': 'RBPmb/3okOKaOTb09WdBjd3zbHHbwKAd+WvWDNaI2dJK87VE'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, proxies=proxies, timeout=10)
        response.raise_for_status()
        res_json = response.json()
    except Exception as e:
        return {"error": str(e)}

    list_aweme_ids = [
        item.get("aweme_id", "")
        for item in res_json.get("aweme_list", [])
        if item.get("aweme_id")
    ]

    return {
        "list_aweme_info_id": list_aweme_ids,
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
    
    url = f"https://oec22-normal-alisg.tiktokv.com/api/v1/shop/recommend/same_shop/get?device_platform=android&os=android&ssmix=a&_rticket=1745198296042&cdid=2af2be00-385e-43eb-af4c-33edf0729808&channel=googleplay&aid=1180&app_name=trill&version_code=390505&version_name=39.5.5&manifest_version_code=390505&update_version_code=390505&ab_version=39.5.5&resolution=900*1600&dpi=320&device_type=SM-S9180&device_brand=samsung&language=vi&os_api=32&os_version=12&ac=wifi&is_pad=0&current_region=VN&app_type=normal&sys_region=VN&last_install_time=1744964235&mcc_mnc=45204&timezone_name=Asia%2FBangkok&carrier_region_v2=452&residence=VN&app_language=vi&carrier_region=VN&timezone_offset=25200&host_abi=arm64-v8a&locale=vi-VN&ac2=wifi5g&uoo=0&op_region=VN&build_number=39.5.5&region=VN&ts=1745198296&iid=7494564208987899655&device_id=6931281686899869190&openudid=0ff8197ac1f2878b"

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
        "enter_from_info": "mall",
        "author_id": data.author_id,
        "seller_id": data.seller_id,
        "product_source_info": 3,
        "traffic_source_list": [3],
        "session_refresh_index":1,
        "experiment":{
            "params_map":{"pdp_shop_entry":"0"}
            },
        "first_source_page":"show_window"
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


def get_product_info(item_id: int)-> dict:
    url = f"https://affiliate.shopee.vn/api/v3/offer/product?item_id={item_id}"

    global proxy_index

    proxy = None
    if PROXY_LIST:
        proxy = PROXY_LIST[proxy_index % len(PROXY_LIST)]
        proxy_index += 1

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        "af-ac-enc-dat": "72b9b677d7ccc770",
        "csrf-token": "WDT1MQ8a-wl1Tn2rqGdIWji32IbGytMmkj6Q",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "x-sap-ri": "16d20068f7bec074acb4df32030181e8b0db4e8fbe8fe431e7f6",
        "x-sap-sec": "Alr+W8RwyzRbmzRblRRzmz5blRRbmz5bmzRxmzRbfz5bmY5xmzRwmzRbmCDOo5zbmzcpm5Rb7z2bmwKJOXWAxK0JDcOEucqqpf0lKDgD564Xqs+yQpKQ+O4y+d+U/6zTz1A4cRiRc8qMKZviTfZzvd8MqMkhFmKQAOox2KJxQHZes51Msi9EwSKzCQELNK1H8zhWhj441zz4cV0WTYSE8m+0Gq+PA1yNwotwMGn20aMVp1+BpH72MVwA9fPMcnTpzw0q1oxZX6lcAp5ToOJ2G4XTdwxpgJ3GGl/i7fVuPWh19UZPh0qnaYFjp4pth4AUvzeSsOAO79w8eNVPuH9PKtHq488wJEM5NG/V3bsxk4dPq2Z3L45PSuzVusQQqHEHg1ejc9Eaf4X22TiDg90a3RwiqPhMvmFKRRARm0N2Keqing3GpTEmSISaaW38/T9aJcAHXv7WnuKVDpLJ9FXBFV1DPp4HvZRbSbRu5T2h1fZ5RTzpMzV23SLMGmQacpKtyi76S/bKmhXgFi1dYBzcdQC8Fmi2tyVglifMbxM/hRUYZ82VudfPl+L1ukvqv7mKvBEgkW3tUmcNN3DWIi3I4z2uFD8Ulr8L7Fk/09uHyI1N1lh2nyNHG8gE3gfIBzFGcHTAO4MDLzEpD5Rgv1Ux3Bup/OygJwmpIEBjNcqBAOdbTicZbBcxU1eTJ354tGNAuSHhdsxKYYqEXpmUz/kyj0MnOkkdtMSWpxkWeGeqFyG/zvwlmnIbzHvDf7YDnHRROnmvkSUCDgXwqwKhHPRhii0Gk+bTgcwaD9j9nxdoIIx+i1zrvHb4YOinrCoUvwxCsUOGRz1QvvXySvBPjJSrdmLR+SxAczic9K5Lpb7zsUgmm7eJFo4y/76gYCJNgmfEYGLwFtokT26xQrV5auZ51+eNiE04nW5r/5CaZoapXh6WXYeaYKQj6xHqIujjr6mY68pIhFkDsyOWu8ORtuYjYwXlZu/JoLmdIEJJrmAqb4zZWhecId8nq/6ANph506IrtZyLUfQVA/vI0PC0jwbLxFDd0v7gp+XAzqQVNdMJxQ3L9jerdrN/vf+OuXYXKb5O6C9HjECKPhsYHG4hfmfFmZZw4nH9Zt4+6ZSK2lSIC8DeWxSIlFZ+wuNDS+NStHLRQWzzEf8CZARsAdKAKshcCtidI1UwJaIpZpyknkHeOLve4Z0mBYNoPDfydSCgYyaw2zx+M4r8BPgIukhW0DZ0X4VJgtAbjOsu1qtKG0M1QxrEgWSLirfRbvqi6d3eCrrfOW9FWzXHDzEfHUlEx0I4R3EDfXPwMWmcLcxbCWwiJnzAvIDwILNzmzRbCQj4wlo/ClHbmzRb4CnOo5zbmzRXmzRbfzRbmi6VOE26cqJk86ZGwi7wsJOEh47JzzRbmg6pv82ovM2hmzRbmzzbyzRzmz5bzzRbmzzbmzRXmzRbfzRbmyUmWijYwCkZG5NlAVImsYXnCikqzzRbmlSLvDrEC82hmzRbmC==",
        "Cookie": "_gcl_au=1.1.1176551775.1744364046; SPC_SI=PbTrZwAAAABCQzBJYkRBad6pQAAAAAAATmY0WU01aUk=; SPC_F=tZu9sdHbwmsbh9O2wNnxVslqGgzFdWAH; REC_T_ID=1dd00a7e-16b8-11f0-9be7-0e32b3093b02; _fbp=fb.1.1744364047509.519812549399897091; SPC_CLIENTID=dFp1OXNkSGJ3bXNizvzzjkjpqtfbuyid; SPC_CDS_CHAT=189d31a9-29ae-46f5-9ddb-773bbc03ddce; _hjSessionUser_868286=eyJpZCI6IjRmYmU4Zjc3LTA5YjMtNWE4NS1hNGI3LTI2ZjhmOTI4MWE4MyIsImNyZWF0ZWQiOjE3NDQzNjUxODc3MjgsImV4aXN0aW5nIjp0cnVlfQ==; _gid=GA1.2.2024227111.1744679163; language=vi; _sapid=d3fdda1ebfd825796909e459ed92c5c92d0899dc5458f433c5a40ec6; _QPWSDCXHZQA=92fb8d98-ff6c-4deb-d7a4-cb6b163f0cb5; REC7iLP4Q=f40e7773-f950-4f4a-8066-61711607d890; _med=refer; _med=affiliates; SPC_ST=.TU42OHRtRHpvMjdUS2luZSn1HPwFb2MRAghGLsVhheUzYNJDKQY1Sfvay9/19PCAxn14nPSmDJjB9Z+WFXaUO8frWucQdaiI5fSCS4cReAYrsQA73tKRRzDieJTH/iTdsxv3ShsD2kXGVQPnv24gMlcLxLJ4AYxhMzVhUmrD/g6o5LvflnghySI9LsXoSkWMXLq1vaiu+bebid/8osh9d3wE9R43p5QpMkrUFzRs1hqrQSvyIKuF6ZRFSz94sNgv; SPC_U=173248446; SPC_R_T_ID=EpVVmVO/59MaVgp0fUrsN8cjPpSfy86yPU/QnIE/mFafWau0wUcqkOofqKU8GqZAzCipx6brovrxn61FNpOornu9WSL+mJcQgOTRSQi4G2/FZTWa4TTByCsYwNRBXH1QapyvaairDQmNeoDEt6ubPypfV78oyJf4QL+5J7li8W4=; SPC_R_T_IV=SzJCbHo4czFSYzFNaVRodA==; SPC_T_ID=EpVVmVO/59MaVgp0fUrsN8cjPpSfy86yPU/QnIE/mFafWau0wUcqkOofqKU8GqZAzCipx6brovrxn61FNpOornu9WSL+mJcQgOTRSQi4G2/FZTWa4TTByCsYwNRBXH1QapyvaairDQmNeoDEt6ubPypfV78oyJf4QL+5J7li8W4=; SPC_T_IV=SzJCbHo4czFSYzFNaVRodA==; _ga_FV78QC1144=GS1.1.1744871394.6.0.1744871394.60.0.0; 173248446_hasShowedPaymentFillingTip=1; SPC_SC_SESSION=gJrARohI/qGrrcC5rKJ6q5qoK8nNbKVtLKvuj1vz8Ey/ajcoF6cwMDJ60/jBKT3L/aUtnGJo1TN6Nv4NXv35b4ukX/aBBDTlJsUP/a6lpKnWxuJAKuXXaJ2zs45tBIuRbshS09Fn94fg8UUCP7AKW5Vek4yw+jyFfcTPk/hzTSJq4wbAtONW3VGOToxdiVw4gFY74trTzsVWDsDwxMdf6/Y7RxLlCOCJgYoxdN+DCyDJVeCwcupAutZ3fDlKlidAl_1_173248446; SPC_STK=LoM7nMU6Y5o82vXUoXXuYrkUi4UAPBbPUuAF7MjnIsvTh3KJiDyiM0MaQxQgQ3nVdYKwXPbCVf3LXtWMkdN7YCht/igxKXggYBY13cIhvCD5GLo34w0t5vyIc2uGzAE95yy63YiGEijYx5ZUYBYbMO40A6tR6cAwWm6D8AH8ak5nM5aDeTmDMn+jH9TxkFmLyXXRhG61Ks/p6nEjJHCaxXcDJxb2dBoLz6SQE3pwhh9qdsK4x16DOjYBBERyDhIB8WxVitRSk/gqL6VIms5hbMIqkxfxmdTlsuBbQHtzMWFyFdVxffn+H2akWDp4xOhvoT5DM+50i3XpUBZX2YfjXeiKbJJLcWjfi+khja11yhDkVq5ZVq00e6HlAA+x0UPToycqs6Gy6yURxlyDNONWsq56Rnje8cXpnPK4ytdehg/zgnwGifiKOVWPh8QtSFrN8S9ibMxdFFyV8TvJGIYIZA==; SC_DFP=cBXheEbELTUJqayhBVCIqhTSETXIaDGd; _ga_3XVGTY3603=GS1.1.1744876596.2.1.1744877594.60.0.0; _gcl_gs=2.1.k1$i1744881116$u121720009; _gcl_aw=GCL.1744881159.Cj0KCQjwzYLABhD4ARIsALySuCScI5FcxG_JS6dLy0244MD0RiYNV9UNNS9n15MJCmkUtTjCq78CLi4aAsYREALw_wcB; _gac_UA-61914164-6=1.1744881159.Cj0KCQjwzYLABhD4ARIsALySuCScI5FcxG_JS6dLy0244MD0RiYNV9UNNS9n15MJCmkUtTjCq78CLi4aAsYREALw_wcB; _dc_gtm_UA-61914164-6=1; SPC_EC=.ajJ6eXBRUWZvaWp1MUcxVus4e2Z+bhSp3gZqXtej+KH828Q9czLW4+fRbnVvCHpnj5pn3Qu94ZcNbt9wZjIddNZpOTsfvWiOaLHb2kFVrlGoF0lObzx1FaTbie4KAJ66cG+02MD0fkzSpOYROiOCnzAOiKlj+rlfzWkg5aQHes0juUjYjyXH8qVyje547gUbhqSCd2HbU6OQRgZuIi6/6uywTmPSJWHX57Yz6BRcpLFkYltDquOsKIIk8xP7s1Wr; AC_CERT_D=U2FsdGVkX1+IVZ/XLtmbwrP4+ScgDelEk1rBKLurWW2D+r8tWB76ZeMzT1acP8SXe2Grmhmm+b+5FMwYQL+LTEsym5v0h8tEJZKLN5JKUiqyDPFxb3xp3a/zwzOYDGpCYXlU9LOgvax/OfkIgSn65Qy9PXv3Tmsfnqnz4dOMskMXeTlP1qV6U2VktLVYhsSLolt9Rf2w/zfAZLFNtUGU0VplSbcisTJ24iKl2rfe70n85yL0H37pB/aYBApFV8tT0hHfq44cUPqYDTFpX0uBl37d0aEpV/OgTozqC0tglg2ehF/hqSJYlmqB1SJZS/9RZrqeZ81h+jpplzNxgajLk2MUGUHcrCSYdFrK+8ixawP52BIZ9tFWEIhACb6IhELqXUpa9rVGyf2Ag+BxITVs5CnDaWUQ/c+jX/9J2i5ImDxsdKdKDNJbnYhbPMmIF2uZHJvWg9qsr+SbNU50ERuQgYikjL1dCHM1pQkJXZDKvSC1y8odKjUiitXu9BddahUrWvX/NmT6r0791OVlLKVnW9PGgUwz0Ob8Wk6GyOZ84JWfdLUFIvPJfll2zimHifKaBt2eYF8K5Vojmkbq7x7SgOMA6GLYppCSC+vrWNLR9rLu0nPOQZMejX3gLxtkPV3gGwDWj52PRh7Z/kHmv1lj/V9OCUMGzaz4IPMLXCRcIcEGAiUy043nz2hwaKRNucMSehybcTkKABQbhfxneNXCj7LSMZoD4qy0tjzMh1Cgel6PVaeMwowc/bSKT4UldJkmyIfXQVHRTZFfpauMN+erTbS+3dHJ84wyvI2Op633YrRPiHJ2bcFjGSE90iR1ogfMDRXN5PY/ygflnzPH2lt3lTzUG4UMsMxRG+GBUogGUHrjTcASgba919HK410g+Uuk2baROi9CPypwGRwEAso9JunypZLDog0I9+ZBbH0Be29meHkjLwBcjIQpEvYFHKzHrCgQMGLnRiy0MD+/sGAT3RSopzPilNkxqhyZVlnwV2yVCaUfrY50w16beuhNo1ObSStpjeBGDY5ncJYTwF/5tPQudg5mEA5fdLqoLuw2QT+U2BVY/d4n3eW1LP3q9Fp6y6ubUmlmCmQmMgv+qoXillE0RcD7+6fg1lg6Cfzyqco=; _ga=GA1.1.1880851022.1744364049; _ga_4GPP1ZXG63=GS1.1.1744884211.17.1.1744884243.28.0.0; shopee_webUnique_ccd=aAaInJozlBQRZpyIY8DlLw%3D%3D%7ClbhNPnGusPuUe6cPmFxmbyYauA2dZHKfVRkJ9A%2BM%2FE8RuR57IL4KcXdmNDpjDJttgoiZXZPOmH46TKHGUpk%3D%7C7kd%2BoqHq8I%2FSpvfb%7C08%7C3; ds=b172421919a6c15151f6369b1f0281df",
    }

    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)

    response.raise_for_status()
    res_json = response.json()

    item = res_json.get("data", {}).get("batch_item_for_item_card_full", {})
    if not item:
        return {"error": "Không tìm thấy sản phẩm"}

    return {
        "item_id": int(item.get("itemid", 0)),
        "shop_id": int(item.get("shopid", 0)),
        "name": item.get("name", ""),
        "time_ago": to_time_ago(item.get("ctime")) if item.get("ctime") else None,
        "sold": int(item.get("sold", 0)),
        "historical_sold": int(item.get("historical_sold", 0)),
        "price": int(item.get("price", 0)),
    }
