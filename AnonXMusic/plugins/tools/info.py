import os
import random
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from typing import Union, Optional
from AnonXMusic import app

shadwophoto = [
    "https://telegra.ph/file/07fd9e0e34bc84356f30d.jpg",
    "https://telegra.ph/file/3c4de59511e179018f902.jpg",
    "https://telegra.ph/file/07fd9e0e34bc84356f30d.jpg",
    "https://telegra.ph/file/3c4de59511e179018f902.jpg"
]

bg_path = "AnonXMusic/assets/AnnieNinfo.png"
font_path = "AnonXMusic/assets/shadowinf.ttf"

INFO_TEXT = """**
❅─────✧❅✦❅✧─────❅
            ✦ ᴜsᴇʀ ɪɴғᴏ ✦

➻ ᴜsᴇʀ ɪᴅ ‣ **`{}`
**➻ ғɪʀsᴛ ɴᴀᴍᴇ ‣ **{}
**➻ ʟᴀsᴛ ɴᴀᴍᴇ ‣ **{}
**➻ ᴜsᴇʀɴᴀᴍᴇ ‣ **{}
**➻ ᴍᴇɴᴛɪᴏɴ ‣ **{}
**➻ ʟᴀsᴛ sᴇᴇɴ ‣ **{}
**➻ ᴅᴄ ɪᴅ ‣ **{}
**➻ ʙɪᴏ ‣ **`{}`

**❅─────✧❅✦❅✧─────❅**
"""  

async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        status = user.status
        return {
            enums.UserStatus.RECENTLY: "Recently",
            enums.UserStatus.LAST_WEEK: "Last week",
            enums.UserStatus.LONG_AGO: "Long time ago",
            enums.UserStatus.OFFLINE: "Offline",
            enums.UserStatus.ONLINE: "Online"
        }.get(status, "Unknown")
    except Exception:
        return "Unknown"

async def get_userinfo_img(bg_path, font_path, user_id, profile_path=None):
    if not os.path.exists(bg_path):
        print(f"Error: Background image '{bg_path}' not found.")
        return None

    if not os.path.exists(font_path):
        print(f"Error: Font file '{font_path}' not found.")
        return None

    try:
        bg = Image.open(bg_path).convert("RGBA")

        if profile_path and os.path.exists(profile_path) and os.path.getsize(profile_path) > 0:
            try:
                img = Image.open(profile_path).convert("RGBA")
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse([(0, 0), img.size], fill=255)
                circular_img = Image.new("RGBA", img.size)
                circular_img.paste(img, (0, 0), mask)
                resized = circular_img.resize((977, 979))
                bg.paste(resized, (1673, 293), resized)
            except Exception as e:
                print(f"Error processing profile image: {e}")

        img_draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype(font_path, 95)
        img_draw.text(
            (460, 1055),
            text=str(user_id).upper(),
            font=font,
            fill=(125, 227, 230),
        )

        path = f"./userinfo_img_{user_id}.png"
        bg.save(path)
        return path
    except Exception as e:
        print(f"Error creating user info image: {e}")
        return None

@app.on_message(filters.command(["info", "userinfo"], prefixes=["/", "!", "."]))
async def userinfo(client: Client, message: Message):
    chat_id = message.chat.id

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user_identifier = message.text.split(None, 1)[1]
        try:
            target_user = await app.get_users(int(user_identifier) if user_identifier.isdigit() else user_identifier)
        except Exception as e:
            await message.reply_text(f"Could not find user: {e}")
            return
    else:
        target_user = message.from_user

    user_id = target_user.id

    try:
        user_info = await app.get_chat(user_id)
        status = await userstatus(user_id)
        dc_id = target_user.dc_id or "Unknown"
        first_name = user_info.first_name or "No first name"
        last_name = user_info.last_name or "No last name"
        username = f"@{user_info.username}" if user_info.username else "No username"
        mention = target_user.mention
        bio = user_info.bio or "No bio set"

        profile_photo_path = None
        if target_user.photo:
            photo_file_id = target_user.photo.big_file_id
            try:
                profile_photo_path = await app.download_media(photo_file_id)
                if not os.path.exists(profile_photo_path) or os.path.getsize(profile_photo_path) == 0:
                    print("Downloaded profile photo is invalid.")
                    profile_photo_path = None
            except Exception as e:
                print(f"Error downloading profile photo: {e}")

        if profile_photo_path:
            welcome_photo = await get_userinfo_img(
                bg_path=bg_path,
                font_path=font_path,
                user_id=user_id,
                profile_path=profile_photo_path,
            )
        else:
            welcome_photo = random.choice(shadwophoto)

        if welcome_photo:
            await app.send_photo(
                chat_id,
                photo=welcome_photo,
                caption=INFO_TEXT.format(
                    user_id,
                    first_name,
                    last_name,
                    username,
                    mention,
                    status,
                    dc_id,
                    bio
                ),
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text("Failed to generate user info image.")

        try:
            if profile_photo_path and os.path.exists(profile_photo_path):
                os.remove(profile_photo_path)
            if welcome_photo and os.path.exists(welcome_photo):
                os.remove(welcome_photo)
        except Exception as e:
            print(f"Error deleting files: {e}")

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")