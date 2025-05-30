import os
import random
import tempfile
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

    msg = await message.reply("Finding an active couple...")

    try:
        # Step 1: Collect recent active user IDs
        active_ids = set()
        async for msg_ in app.get_chat_history(message.chat.id, limit=200):
            if msg_.from_user and not msg_.from_user.is_bot:
                active_ids.add(msg_.from_user.id)

        active_ids = list(active_ids)
        if len(active_ids) < 2:
            return await msg.edit("Not enough active users found in recent messages.")

        # Step 2: Randomly choose 2
        c1, c2 = random.sample(active_ids, 2)
        user1, user2 = await app.get_users([c1, c2])

        name1 = user1.mention
        name2 = user2.mention

        async def get_photo_or_fallback(user):
            if user.photo:
                try:
                    return await app.download_media(user.photo.big_file_id)
                except:
                    return FALLBACK_PFP
            return FALLBACK_PFP

        p1 = await get_photo_or_fallback(user1)
        p2 = await get_photo_or_fallback(user2)

        img1 = circle_avatar(p1)
        img2 = circle_avatar(p2)

        template = Image.open(TEMPLATE_PATH).convert("RGBA")
        template.paste(img1, (75, 65), img1)
        template.paste(img2, (265, 65), img2)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
            out_path = temp_img.name
            template.save(out_path)

        _, tomorrow = get_today_tomorrow()
        chat_title = message.chat.title or "this group"

        caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑨𝒄𝒕𝒊𝒗𝒆 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {chat_title}
╰• ☞  𝑵𝒆𝒙𝒕 𝒍𝒖𝒄𝒌𝒚 𝒑𝒂𝒊𝒓 𝒘𝒉𝒆𝒏 𝒚𝒐𝒖 𝒓𝒖𝒏 /couples 𝒂𝒈𝒂𝒊𝒏 ♥"""

        await message.reply_photo(out_path, caption=caption)
        await msg.delete()

        # Cleanup
        for file in [p1, p2, out_path]:
            try:
                if file and os.path.exists(file) and "upic.png" not in file:
                    os.remove(file)
            except:
                pass

    except Exception as e:
        await msg.edit(f"Something went wrong: {e}")