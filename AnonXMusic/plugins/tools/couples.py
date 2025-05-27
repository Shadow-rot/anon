import os
import io
import random
import asyncio
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatType
from motor.motor_asyncio import AsyncIOMotorClient
from AnonXMusic import app

mongo = AsyncIOMotorClient(os.environ.get("MONGO_DB_URI"))
couples_col = mongo.AnonXMusic.couples

TEMPLATE_PATH = "AnonXMusic/assets/Couples.jpg"
FALLBACK_PFP = "AnonXMusic/assets/upic.png"

def get_today_tomorrow():
    now = datetime.now()
    return now.strftime("%d/%m/%Y"), (now + timedelta(days=1)).strftime("%d/%m/%Y")

def circle_avatar(image_bytes, size=(135, 135)):
    img = Image.open(image_bytes).convert("RGBA").resize(size)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, *size), fill=255)
    img.putalpha(mask)
    return img

@app.on_message(filters.command("couples"))
async def couples_handler(_, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")

    msg = await message.reply("Picking today's couple...")

    try:
        group_id = str(message.chat.id)
        today, tomorrow = get_today_tomorrow()

        # Check DB for today's couple
        doc = await couples_col.find_one({"group_id": group_id, "date": today})
        if doc:
            caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {doc['name1']} + {doc['name2']} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""
            return await message.reply(caption)

        # Get recent active users
        users = set()
        async for msg in app.get_chat_history(message.chat.id, limit=100):
            if msg.from_user and not msg.from_user.is_bot:
                users.add(msg.from_user.id)

        users = list(users)
        if len(users) < 2:
            return await msg.edit("Not enough active members found.")

        # Pick random couple
        uid1, uid2 = random.sample(users, 2)
        user1, user2 = await app.get_users([uid1, uid2])
        name1, name2 = user1.mention, user2.mention

        async def fetch_pic(user):
            if user.photo:
                try:
                    return await app.download_media(user.photo.big_file_id, in_memory=True)
                except:
                    pass
            return open(FALLBACK_PFP, "rb")

        p1_bytes, p2_bytes = await asyncio.gather(fetch_pic(user1), fetch_pic(user2))
        img1, img2 = circle_avatar(p1_bytes), circle_avatar(p2_bytes)

        # Create final image
        base = Image.open(TEMPLATE_PATH).convert("RGBA")
        base.paste(img1, (75, 65), img1)
        base.paste(img2, (265, 65), img2)

        output = io.BytesIO()
        output.name = "couple.png"
        base.save(output, format="PNG")
        output.seek(0)

        # Caption
        caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""

        await message.reply_photo(output, caption=caption)
        await msg.delete()

        # Save to DB in background
        await couples_col.insert_one({
            "group_id": group_id,
            "date": today,
            "name1": name1,
            "name2": name2
        })

    except Exception as e:
        await msg.edit(f"Error: {e}")