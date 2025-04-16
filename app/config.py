from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("TIKTOK_API_URL")
DEVICE_ID = os.getenv("TIKTOK_DEVICE_ID")
AID = os.getenv("TIKTOK_AID")
LOCALE = os.getenv("TIKTOK_LOCALE")
TIKTOK_COOKIE = os.getenv("TIKTOK_COOKIE")

SHOPEE_COOKIE = os.getenv("SHOPEE_COOKIE")

SOLD_TIKTOK_COOKIE = os.getenv("SOLD_TIKTOK_COOKIE")

