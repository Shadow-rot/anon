"""
import os
import random
from datetime import datetime
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatType
from AnonXMusic import app

TEMPLATE_PATH = "AnonXMusic/assets/Couples.jpg"
FALLBACK_PFP = "AnonXMusic/assets/upic.png"

def get_today_tomorrow():
    now = datetime.now()
    today = now.strftime("%d/%m/%Y")
    tomorrow = (now.replace(day=now.day + 1)).strftime("%d/%m/%Y")
    return today, tomorrow

@app.on_message(filters.command("couples"))
async def couples_handler(_, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")

    msg = await message.reply("Picking today's couple...")

    try:
        users = [
            member.user.id async for member in app.get_chat_members(message.chat.id, limit=50)
            if not member.user.is_bot
        ]
        if len(users) < 2:
            return await msg.edit("Not enough members to select a couple.")

        c1, c2 = random.sample(users, 2)
        user1, user2 = await app.get_users([c1, c2])
        name1 = user1.mention
        name2 = user2.mention

        photo1 = user1.photo.big_file_id if user1.photo else None
        photo2 = user2.photo.big_file_id if user2.photo else None

        p1 = await app.download_media(photo1) if photo1 else FALLBACK_PFP
        p2 = await app.download_media(photo2) if photo2 else FALLBACK_PFP

        def process_pfp(path):
            size = (135, 135)  # Even smaller for perfect overlay
            img = Image.open(path).convert("RGBA").resize(size)
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)
            return img

        img1 = process_pfp(p1)
        img2 = process_pfp(p2)

        template = Image.open(TEMPLATE_PATH).convert("RGBA")
        template.paste(img1, (75, 65), img1)   # Adjusted for new size
        template.paste(img2, (265, 65), img2)

        out_path = f"temp_couple_{message.chat.id}.png"
        template.save(out_path)

        today, tomorrow = get_today_tomorrow()

      """  caption = f"""╭─❍ 𝑻𝒐𝒅𝒂𝒚'𝒔 𝑪𝒖𝒕𝒆𝒔𝒕 𝑪𝒐𝒖𝒑𝒍𝒆 ♥
│ • {name1} + {name2} = 𝑳𝒐𝒗𝒆𝒃𝒊𝒓𝒅𝒔
│ • 𝑮𝒓𝒐𝒖𝒑: {message.chat.title}
╰• ☞ 𝑵𝒆𝒙𝒕 𝒑𝒂𝒊𝒓 𝒐𝒏 {tomorrow}
"""

        await message.reply_photo(out_path, caption=caption)
        await msg.delete()

        try:
            link = upload_file(out_path)[0]
            print("Telegraph URL:", "https://graph.org/" + link)
        except:
            pass

    except Exception as e:
        await msg.edit(f"Error: {e}")
    finally:
        for f in [p1, p2, out_path]:
            try:
                if os.path.exists(f) and "upic.png" not in f:
                    os.remove(f)
            except:
                pass
""" """