# AnonXMusic/utils/harem_db.py

from motor.motor_asyncio import AsyncIOMotorClient

HAREM_URI = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

harem_client = AsyncIOMotorClient(HAREM_URI)

harem_db = harem_client["harem_data"]
harem_collection = harem_db["characters"]
harem_users = harem_db["users"]