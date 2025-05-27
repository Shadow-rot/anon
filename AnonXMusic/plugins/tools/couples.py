import os
import random
import tempfile
from datetime import datetime, timedelta
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from AnonXMusic import app
from AnonXMusic.config import MONGO_DB_URI

# DB setup
mongo = AsyncIOMotorClient(MONGO_DB_URI)
couples_col = mongo.AnonXMusic.couples

TEMPLATE_PATH = "AnonXMusic/assets/Couples.jpg"
FALLBACK_PFP = "AnonXMusic/assets/upic.png"

def get_today_tomorrow():
    now = datetime.now()
    today = now.strftime("%d/%m/%Y")
    tomorrow = (now + timedelta(days=1)).strftime("%d/%m/%Y")
    return today, tomorrow

def circle_avatar(image_path, size=(135, 135)):
    img = Image.open(image_path).convert("RGBA").resize(size)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

@app.on_message(filters.command("couples"))
async def couples_handler(_, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")

    msg = await message.reply("Finding today's couple...")

    try:
        group_id = str(message.chat.id)
        today, tomorrow = get_today_tomorrow()

        # Check if already selected
        doc = await couples_col.find_one({"group_id": group_id, "date": today})
        if doc:
            name1, name2 = doc["name1"], doc["name2"]
            img_url = doc.get("telegraph_url")
            caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("View Image", url=img_url)]]
            ) if img_url else None
            return await message.reply(caption, reply_markup=buttons)

        users = [
            m.user.id async for m in app.get_chat_members(message.chat.id, limit=100)
            if not m.user.is_bot
        ]
        if len(users) < 2:
            return await msg.edit("Not enough users to choose a couple.")

        c1, c2 = random.sample(users, 2)
        user1, user2 = await app.get_users([c1, c2])
        name1 = user1.mention
        name2 = user2.mention

        async def get_photo(user):
            if user.photo:
                try:
                    return await app.download_media(user.photo.big_file_id)
                except:
                    pass
            return FALLBACK_PFP

        p1 = await get_photo(user1)
        p2 = await get_photo(user2)

        img1 = circle_avatar(p1)
        img2 = circle_avatar(p2)

        template = Image.open(TEMPLATE_PATH).convert("RGBA")
        template.paste(img1, (75, 65), img1)
        template.paste(img2, (265, 65), img2)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            out_path = tmp.name
            template.save(out_path)

        caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""

        telegraph_url = None
        try:
            tg_path = upload_file(out_path)[0]
            telegraph_url = f"https://graph.org/{tg_path}"
        except Exception as e:
            print("Telegraph upload failed:", e)

        # Save to DB
        await couples_col.insert_one({
            "group_id": group_id,
            "date": today,
            "name1": name1,
            "name2": name2,
            "telegraph_url": telegraph_url
        })

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("View Image", url=telegraph_url)]]
        ) if telegraph_url else None

        await message.reply_photo(out_path, caption=caption, reply_markup=buttons)
        await msg.delete()

    except Exception as e:
        await msg.edit(f"Something went wrong: {e}")

    finally:
        for f in [p1, p2, locals().get("out_path")]:
            if f and os.path.exists(f) and "upic.png" not in f:
                try:
                    os.remove(f)
                except:
                    pass