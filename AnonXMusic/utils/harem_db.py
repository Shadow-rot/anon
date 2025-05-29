from motor.motor_asyncio import AsyncIOMotorClient

# Mongo URI for Harem system
HAREM_URI = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client
harem_client = AsyncIOMotorClient(HAREM_URI)

# Database for harem/shop system
harem_db = harem_client["harem_data"]

# Collections
collection = harem_db["characters"]     # Stores waifu/character data
harem_users = harem_db["users"]         # Stores user economy, xp, harem, etc.
db = harem_db                           # For any extra collections like sequences

# Optional: create sequence counter collection if not exists
# This is used for auto-incrementing character IDs
sequences = harem_db["sequences"]