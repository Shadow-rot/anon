import random
import string
import time
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app  # adjust if your app object has a different import

user_data = {}  # Memory storage
redeem_codes = {}

OWNER_ID = 5147822244  # replace with your Telegram user ID

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "xp": 0, "last_claim": None}
    return user_data[user_id]

@app.on_message(filters.command("bal"))
async def balance(_, message: Message):
    user = get_user(message.from_user.id)
    await message.reply(f"Your Balance: $ `{user['balance']}` Gold coins 💰", quote=True)

@app.on_message(filters.command("pay"))
async def pay(_, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to pay Gold coins.")

    try:
        amount = int(message.command[1])
    except:
        return await message.reply("Usage: /pay <amount> (reply to someone)")

    sender_id = message.from_user.id
    recipient_id = message.reply_to_message.from_user.id

    if sender_id == recipient_id:
        return await message.reply("You can't pay yourself.")

    sender = get_user(sender_id)
    recipient = get_user(recipient_id)

    if sender["balance"] < amount:
        return await message.reply("Not enough Gold coins.")

    sender["balance"] -= amount
    recipient["balance"] += amount

    await message.reply(f"Paid $ `{amount}` to {message.reply_to_message.from_user.mention} 💸")

@app.on_message(filters.command("claim"))
async def claim(_, message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    now = datetime.utcnow()
    last = user["last_claim"]

    if last and (now - last) < timedelta(hours=24):
        wait = timedelta(hours=24) - (now - last)
        return await message.reply(f"Already claimed. Wait `{str(wait).split('.')[0]}`.")

    user["balance"] += 2000
    user["last_claim"] = now
    await message.reply("🎁 Claimed 2000 Gold coins!")

@app.on_message(filters.command("roll"))
async def roll(_, message: Message):
    try:
        amount = int(message.command[1])
        guess = message.command[2].upper()
        assert guess in ("ODD", "EVEN")
    except:
        return await message.reply("Usage: /roll <amount> <ODD/EVEN>")

    user = get_user(message.from_user.id)
    if user["balance"] < amount:
        return await message.reply("Not enough balance to roll.")

    dice = random.randint(1, 6)
    result = "EVEN" if dice % 2 == 0 else "ODD"

    if result == guess:
        user["balance"] += amount
        user["xp"] += 4
        msg = f"🎲 Dice: {dice} ({result})\n✅ Won {amount} coins! XP +4"
    else:
        user["balance"] -= amount
        user["xp"] -= 2
        msg = f"🎲 Dice: {dice} ({result})\n❌ Lost {amount} coins. XP -2"

    await message.reply(msg)

@app.on_message(filters.command("xp"))
async def xp(_, message: Message):
    user = get_user(message.from_user.id)
    xp = user["xp"]
    level = int((xp / 100) ** 0.5) + 1

    await message.reply(f"🎚 Level: {level}\n⭐ XP: {xp}")

@app.on_message(filters.command("tophunters"))
async def tophunters(_, message: Message):
    top = sorted(user_data.items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
    msg = "🏆 Top 10 Hunters:\n\n"
    for i, (uid, data) in enumerate(top, 1):
        msg += f"{i}. [{uid}](tg://user?id={uid}) — $ `{data['balance']}`\n"
    await message.reply(msg, parse_mode="markdown")

@app.on_message(filters.command("generatecode") & filters.user(OWNER_ID))
async def generate(_, message: Message):
    try:
        amount = int(message.command[1])
    except:
        return await message.reply("Usage: /generatecode <amount>")

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    redeem_codes[code] = amount

    await message.reply(f"🎟 Code generated: `{code}`\nWorth: $ `{amount}` coins")

@app.on_message(filters.command("redeem"))
async def redeem(_, message: Message):
    try:
        code = message.command[1].upper()
    except:
        return await message.reply("Usage: /redeem <code>")

    if code not in redeem_codes:
        return await message.reply("Invalid or already used code.")

    amount = redeem_codes.pop(code)
    user = get_user(message.from_user.id)
    user["balance"] += amount

    await message.reply(f"✅ Redeemed code `{code}` for $ `{amount}` coins!")