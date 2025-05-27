import io
import os
import random
import asyncio
from datetime import datetime, timedelta
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from AnonXMusic import app
from AnonXMusic.config import MONGO_DB_URI
mongo = AsyncIOMotorClient(os.environ.get("MONGO_DB_URI"))
couples_col = mongo.AnonXMusic.couples

TEMPLATE_PATH = "AnonXMusic/assets/Couples.jpg"
FALLBACK_PFP = "AnonXMusic/assets/upic.png"

def get_today_tomorrow():
    now = datetime.now()
    return now.strftime("%d/%m/%Y"), (now + timedelta(days=1)).strftime("%d/%m/%Y")

def circle_avatar(img_bytes, size=(135, 135)):
    img = Image.open(img_bytes).convert("RGBA").resize(size)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, *size), fill=255)
    img.putalpha(mask)
    return img

@app.on_message(filters.command("couples"))
async def fast_couples(_, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")

    msg = await message.reply("Picking a cute couple...")

    try:
        group_id = str(message.chat.id)
        today, tomorrow = get_today_tomorrow()

        # Return early if couple is cached
        doc = await couples_col.find_one({"group_id": group_id, "date": today})
        if doc:
            caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {doc['name1']} + {doc['name2']} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""
            if doc.get("telegraph_url"):
                btn = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("View Image", url=doc["telegraph_url"])]]
                )
                return await message.reply(caption, reply_markup=btn)
            return await message.reply(caption)

        # Get recent active users (faster than get_chat_members)
        users = set()
        async for msg in app.get_chat_history(message.chat.id, limit=100):
            if msg.from_user and not msg.from_user.is_bot:
                users.add(msg.from_user.id)
        users = list(users)
        if len(users) < 2:
            return await msg.edit("Not enough active users found.")

        c1, c2 = random.sample(users, 2)
        user1, user2 = await app.get_users([c1, c2])
        name1 = user1.mention
        name2 = user2.mention

        async def fetch_photo(user):
            if user.photo:
                try:
                    return await app.download_media(user.photo.big_file_id, in_memory=True)
                except:
                    pass
            return open(FALLBACK_PFP, "rb")

        p1_data, p2_data = await asyncio.gather(
            fetch_photo(user1), fetch_photo(user2)
        )

        img1 = circle_avatar(p1_data)
        img2 = circle_avatar(p2_data)

        template = Image.open(TEMPLATE_PATH).convert("RGBA")
        template.paste(img1, (75, 65), img1)
        template.paste(img2, (265, 65), img2)

        output = io.BytesIO()
        output.name = "couple.png"
        template.save(output, format="PNG")
        output.seek(0)

        caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""

        sent_msg = await message.reply_photo(output, caption=caption)
        await msg.delete()

        # Telegraph (optional + after reply to avoid delay)
        async def save_to_db():
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    template.save(f.name)
                    tg = upload_file(f.name)[0]
                    url = f"https://graph.org/{tg}"
                    os.remove(f.name)
            except:
                url = None

            await couples_col.insert_one({
                "group_id": group_id,
                "date": today,
                "name1": name1,
                "name2": name2,
                "telegraph_url": url
            })

        asyncio.create_task(save_to_db())

    except Exception as e:
        await msg.edit(f"Error: {e}")