import os
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatType
from AnonXMusic import app

TEMPLATE_PATH = "AnonXMusic/assets/Couples.jpg"
FALLBACK_PFP = "AnonXMusic/assets/upic.png"


def get_today_tomorrow():
    now = datetime.now()
    today = now.strftime("%d/%m/%Y")
    tomorrow = (now + timedelta(days=1)).strftime("%d/%m/%Y")
    return today, tomorrow


def make_circle(img_path):
    size = (135, 135)
    img = Image.open(img_path).convert("RGBA").resize(size)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img


@app.on_message(filters.command("couples") & filters.group)
async def couples_handler(_, message):
    msg = await message.reply("Choosing today’s cutest couple...")

    try:
        users = [
            member.user.id async for member in app.get_chat_members(message.chat.id, limit=50)
            if not member.user.is_bot and not member.user.is_deleted
        ]
        if len(users) < 2:
            return await msg.edit("Not enough active members to choose a couple.")

        c1, c2 = random.sample(users, 2)
        user1, user2 = await app.get_users([c1, c2])

        name1 = user1.mention
        name2 = user2.mention

        p1_path = FALLBACK_PFP
        p2_path = FALLBACK_PFP

        if user1.photo:
            try:
                p1_path = await app.download_media(user1.photo.big_file_id)
            except:
                pass

        if user2.photo:
            try:
                p2_path = await app.download_media(user2.photo.big_file_id)
            except:
                pass

        img1 = make_circle(p1_path)
        img2 = make_circle(p2_path)

        template = Image.open(TEMPLATE_PATH).convert("RGBA")
        template.paste(img1, (75, 65), img1)
        template.paste(img2, (265, 65), img2)

        out_path = f"temp/couple_{message.chat.id}_{random.randint(1, 9999)}.png"
        os.makedirs("temp", exist_ok=True)
        template.save(out_path)

        today, tomorrow = get_today_tomorrow()

        caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""

        await message.reply_photo(out_path, caption=caption)
        await msg.delete()

    except Exception as e:
        await msg.edit(f"Error: {e}")

    finally:
        for f in [p1_path, p2_path, out_path]:
            try:
                if os.path.exists(f) and "upic.png" not in f:
                    os.remove(f)
            except:
                pass