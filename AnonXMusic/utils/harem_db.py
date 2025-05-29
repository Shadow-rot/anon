from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection URI
HAREM_URI = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB using Motor
harem_client = AsyncIOMotorClient(HAREM_URI)

# Use a separate database (not affecting your main one)
harem_db = harem_client["harem_data"]

# Collections for characters and users
harem_collection = harem_db["characters"]
harem_users = harem_db["users"]