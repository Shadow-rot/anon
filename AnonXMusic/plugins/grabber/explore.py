import random
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic import app
from AnonXMusic.utils.data import users_col

# Cooldown tracking
COOLDOWN_DURATION = 73  # in seconds
COMMAND_COST = 300
REWARD_MIN = 600
REWARD_MAX = 1000

# In-memory cooldown dict
user_cooldowns = {}

@app.on_message(filters.command("explore") & filters.private | filters.group)
async def explore_command(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Don't allow replying to others
    if message.reply_to_message:
        return await message.reply_text("❌ This command can't be used as a reply.")

    # Cooldown check
    last_used = user_cooldowns.get(user_id)
    now = datetime.utcnow()
    if last_used and (now - last_used).total_seconds() < COOLDOWN_DURATION:
        remaining = int(COOLDOWN_DURATION - (now - last_used).total_seconds())
        return await message.reply_text(f"⏳ Please wait {remaining} seconds before exploring again.")

    # Fetch user balance
    user_data = await users_col.find_one({'id': user_id}, projection={'balance': 1})
    balance = user_data.get('balance', 0) if user_data else 0

    if balance < COMMAND_COST:
        return await message.reply_text("💰 You need at least 300 tokens to explore!")

    # Deduct entry fee
    await users_col.update_one({'id': user_id}, {'$inc': {'balance': -COMMAND_COST}})

    # Reward random tokens
    reward = random.randint(REWARD_MIN, REWARD_MAX)
    await users_col.update_one({'id': user_id}, {'$inc': {'balance': reward}})

    # Update cooldown
    user_cooldowns[user_id] = now

    # Random message
    explore_scenarios = [
        "explored a hidden dungeon",
        "ventured into a dark forest",
        "found ancient ruins",
        "visited an elvish village",
        "raided a goblin nest",
        "sneaked into an orc den"
    ]
    scenario = random.choice(explore_scenarios)

    await message.reply_text(f"🗺️ You {scenario} and found 💰 {reward} tokens!")