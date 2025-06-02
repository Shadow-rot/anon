# AnonXMusic/utils/database.py

import motor.motor_asyncio

# Your MongoDB connection string
MONGO_URL = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize Mongo client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Main database
db = client["anonxmusic_db"]

# General economy users
users_col = db["users"]

# Grabber-specific collections
characters_col = db["characters"]
harem_col = db["harems"]
store_col = db["store"]  # optional if used in grabber shop
claimed_col = db["claimed"]  # optional if used in grabber logic
daily_col = db["daily"]      # optional for daily reward logic
collection = db['anime_characters']
user_totals_collection = db['user_totals']
group_user_totals_collection = db['group_user_total']
top_global_groups_collection = db['top_global_groups']

# Add other collections as needed for future features