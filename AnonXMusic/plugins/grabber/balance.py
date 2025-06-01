from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import math
import random

from AnonXMusic import app
from AnonXMusic.utils.data import users_col  # Make sure this points to your MongoDB collection

# ========== BALANCE ==========
@app.on_message(filters.command("bal"))
async def balance(_, message: Message):
    user_id = message.from_user.id
    user_data = await users_col.find_one({'id': user_id})
    if user_data:
        balance_amount = user_data.get('balance', 0)
        await message.reply_text(f"Your Current Balance Is :  $ `{balance_amount}` Gold coins!!")
    else:
        await message.reply_text("You are not eligible To be a Hunter 🍂")

# ========== PAY ==========
pay_cooldown = {}

@app.on_message(filters.command("pay") & filters.reply)
async def pay(_, message: Message):
    sender_id = message.from_user.id
    recipient = message.reply_to_message.from_user

    if recipient.id == sender_id:
        return await message.reply_text("You can't give $ Gold coins To Yourself!")

    if sender_id in pay_cooldown:
        last_time = pay_cooldown[sender_id]
        if (datetime.utcnow() - last_time) < timedelta(minutes=30):
            return await message.reply_text("You can pay /pay again after 30 Minutes!!...")

    try:
        amount = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply_text("Invalid amount, use `/pay <amount>`")

    if amount <= 0:
        return await message.reply_text("Amount must be positive BKL !!!")
    elif amount > 1_000_000:
        return await message.reply_text("You can pay up to $ `10,00,000` Gold coins in one payment !!")

    sender_data = await users_col.find_one({'id': sender_id})
    if not sender_data or sender_data.get('balance', 0) < amount:
        return await message.reply_text("Insufficient amount to pay !!.")

    await users_col.update_one({'id': sender_id}, {'$inc': {'balance': -amount}})
    await users_col.update_one({'id': recipient.id}, {'$inc': {'balance': amount}}, upsert=True)

    pay_cooldown[sender_id] = datetime.utcnow()
    username = recipient.username or f"user{recipient.id}"
    await message.reply_text(
        f"Success! You paid $ `{amount}` Gold coins to [{recipient.first_name}](https://t.me/{username})!",
        disable_web_page_preview=True
    )

# Top Hunters
@app.on_message(filters.command("mtop"))
async def mtop(_, message: Message):
    top_users = await users_col.find({}, projection={'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}) \
                                     .sort('balance', -1).limit(10).to_list(10)

    text = "🏆 Top 10 Rich Hunters:\n\n"
    for i, user in enumerate(top_users, start=1):
        name = user.get("first_name", "Unknown")
        if user.get("last_name"):
            name += f" {user['last_name']}"
        balance = user.get("balance", 0)
        text += f"{i}. {name} — $ {balance} Gold Coins\n"

    await message.reply_photo(
        photo="https://telegra.ph/file/07283c3102ae87f3f2833.png",
        caption=text  # parse_mode removed
    )

# ========== CLAIM DAILY ==========
@app.on_message(filters.command("claim"))
async def daily_reward(_, message: Message):
    user_id = message.from_user.id
    now = datetime.utcnow()

    user_data = await users_col.find_one({'id': user_id})
    last_claim = user_data.get("last_daily_reward") if user_data else None

    if last_claim and last_claim.date() == now.date():
        delta = timedelta(days=1) - (now - last_claim)
        hours, rem = divmod(delta.seconds, 3600)
        mins, secs = divmod(rem, 60)
        return await message.reply_text(f"Already claimed! Try again in `{hours}h {mins}m {secs}s`.")

    await users_col.update_one(
        {'id': user_id},
        {'$inc': {'balance': 2000}, '$set': {'last_daily_reward': now}},
        upsert=True
    )
    await message.reply_text("Congratulations! You claimed $ `2000` Gold coins as a daily reward.")

# ========== ROLL ==========
@app.on_message(filters.command("roll"))
async def roll(_, message: Message):
    user_id = message.from_user.id
    try:
        amount = int(message.command[1])
        choice = message.command[2].upper()
    except (IndexError, ValueError):
        return await message.reply_text("Usage: /roll <amount> <ODD/EVEN>")

    if amount < 0:
        return await message.reply_text("Amount must be positive.")

    user_data = await users_col.find_one({'id': user_id})
    if not user_data:
        return await message.reply_text("User data not found.")

    balance = user_data.get("balance", 0)
    if amount > balance:
        return await message.reply_text("Insufficient balance to place the bet.")
    if amount < balance * 0.07:
        return await message.reply_text("You must bet more than 7% of your balance.")

    # FIXED: use message._client to send dice
    dice = await message._client.send_dice(message.chat.id, "🎲")
    value = dice.dice.value
    result = "ODD" if value % 2 else "EVEN"

    xp_change = 4 if choice == result else -2
    balance_change = amount if choice == result else -amount

    await users_col.update_one(
        {'id': user_id},
        {'$inc': {'balance': balance_change, 'user_xp': xp_change}}
    )

    outcome_msg = f"Dice rolled: {value} ({result})\n"
    if choice == result:
        outcome_msg += f"You won! Gained $ `{amount * 2}`."
    else:
        outcome_msg += f"You lost! Lost $ `{amount}`."

    await message.reply_text(f"{outcome_msg}\nXP change: {xp_change}")

# ========== XP ==========
@app.on_message(filters.command("xp"))
async def xp(_, message: Message):
    user_id = message.from_user.id
    user_data = await users_col.find_one({'id': user_id})

    if not user_data:
        return await message.reply_text("User data not found.")

    xp = user_data.get("user_xp", 0)
    level = min(100, math.floor(math.sqrt(xp / 100)) + 1)

    ranks = {1: "E", 10: "D", 30: "C", 50: "B", 70: "A", 90: "S"}
    rank = next((r for l, r in ranks.items() if level <= l), "S+")

    await message.reply_text(f"Your current level is `{level}`\nand your rank is `{rank}`.")