import os
import random
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
from pyrogram import Client, filters, enums
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, Message
from typing import Union, Optional
from logging import getLogger
from datetime import datetime, timedelta, timezone

from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

LOGGER = getLogger(__name__)


class WelDatabase:
    def __init__(self):
        self.data = {}
        self.join_counts = {}
        self.join_timestamps = {}
        self.auto_disabled = {}

    async def find_one(self, chat_id):
        return self.data.get(chat_id, {"state": "on"})

    async def set_state(self, chat_id, state):
        self.data[chat_id] = {"state": state}

    async def is_welcome_on(self, chat_id):
        chat_data = await self.find_one(chat_id)
        return chat_data.get("state") == "on"

    async def track_join(self, chat_id):
        now = datetime.now(timezone.utc)
        last_join_time = self.join_timestamps.get(chat_id, now)
        if (now - last_join_time).total_seconds() > 8:
            self.join_counts[chat_id] = 1
        else:
            self.join_counts[chat_id] = self.join_counts.get(chat_id, 0) + 1
        self.join_timestamps[chat_id] = now
        return self.join_counts[chat_id]

    async def auto_disable_welcome(self, chat_id):
        await self.set_state(chat_id, "off")
        self.auto_disabled[chat_id] = datetime.now(timezone.utc) + timedelta(minutes=30)

    async def check_auto_reenable(self, chat_id):
        disable_time = self.auto_disabled.get(chat_id)
        if disable_time and datetime.now(timezone.utc) >= disable_time:
            await self.set_state(chat_id, "on")
            del self.auto_disabled[chat_id]
            return True
        return False

wlcm = WelDatabase()

class temp:
    MELCOW = {}

def circle(pfp, size=(220, 220)):
    pfp = pfp.resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    mask = mask.resize(pfp.size, Image.LANCZOS)
    pfp.putalpha(mask)
    return pfp


def welcomepic(pic_path, user, chatname, user_id, uname):
    background = Image.open("AnonXMusic/assets/Welcome.jpg")
    pfp = Image.open(pic_path).convert("RGBA")

    # New size to match white circle (estimated around 420x420)
    circle_size = (220, 220)
    pfp = circle(pfp, size=circle_size)

    draw = ImageDraw.Draw(background)
    font_large = ImageFont.truetype('AnonXMusic/assets/ArialReg.ttf', size=65)

    # New position to match the white circle on the image
    pfp_position = (70, 190)  # Adjust as needed for perfect fit

    draw.text((421, 715), f'{user}', fill=(242, 242, 242), font=font_large)
    draw.text((270, 1005), f'{user_id}', fill=(242, 242, 242), font=font_large)
    draw.text((570, 1308), f"{uname}", fill=(242, 242, 242), font=font_large)

    background.paste(pfp, pfp_position, pfp)
    image_path = f"downloads/welcome#{user_id}.png"
    background.save(image_path)
    return image_path


@app.on_message(filters.command("wel") & ~filters.private)
async def auto_state(client, message):
    usage = "**Usage:**\n⦿/wel [on|off]\n➤ANNIE SPECIAL WELCOME.........."
    if len(message.command) != 2:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user_status = await client.get_chat_member(chat_id, message.from_user.id)
    if user_status.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("**sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ sᴛᴀᴛᴜs!**")

    state = message.text.split(None, 1)[1].strip().lower()
    current_state = await wlcm.find_one(chat_id)
    if state == "off":
        if current_state.get("state") == "off":
            await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
        else:
            await wlcm.set_state(chat_id, "off")
            await message.reply_text(f"**ᴅɪsᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")
    elif state == "on":
        if current_state.get("state") == "on":
            await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**")
        else:
            await wlcm.set_state(chat_id, "on")
            await message.reply_text(f"**ᴇɴᴀʙʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}**")
    else:
        await message.reply_text(usage)


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(client, member: ChatMemberUpdated):
    chat_id = member.chat.id
    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    welcome_enabled = await wlcm.is_welcome_on(chat_id)
    if not welcome_enabled:
        auto_reenabled = await wlcm.check_auto_reenable(chat_id)
        if auto_reenabled:
            await client.send_message(
                chat_id,
                "**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇ-ᴇɴᴀʙʟᴇᴅ.**"
            )
        else:
            return

    join_count = await wlcm.track_join(chat_id)
    if join_count >= 10:
        await wlcm.auto_disable_welcome(chat_id)
        await client.send_message(
            chat_id,
            "ᴍᴀssɪᴠᴇ ᴊᴏɪɴ ᴅᴇᴛᴇᴄᴛᴇᴅ. ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʀᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ 30 ᴍɪɴᴜᴛᴇs."
        )
        return

    if member.new_chat_member and member.new_chat_member.status == enums.ChatMemberStatus.MEMBER:
        try:
            pic_path = None
            if user.photo:
                pic_path = await client.download_media(
                    user.photo.big_file_id, file_name=f"downloads/pp{user.id}.png"
                )
            else:
                pic_path = "AnonXMusic/assets/upic.png"

            previous_message = temp.MELCOW.get(f"welcome-{chat_id}")
            if previous_message:
                try:
                    await previous_message.delete()
                except Exception as e:
                    LOGGER.error(f"Error deleting previous welcome message: {e}")

            welcome_img = welcomepic(
                pic_path, user.first_name, member.chat.title, user.id, user.username or "No Username"
            )

            count = await client.get_chat_members_count(chat_id)
            button_text = "๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏"
            add_button_text = "๏ ᴋɪᴅɴᴀᴘ ᴍᴇ ๏"
            deep_link = f"tg://openmessage?user_id={user.id}"
            add_link = f"https://t.me/{client.username}?startgroup=true"
            welcome_message = await client.send_photo(
                chat_id,
                photo=welcome_img,
                caption=f"""
𓆩✦ 𝓐 𝓝𝓮𝔀 𝓢𝓽𝓪𝓻 𝓗𝓪𝓼 𝓔𝓷𝓽𝓮𝓻𝓮𝓭 𝓞𝓾𝓻 𝓢𝓴𝔂 ✦𓆪  
 ━❖ {member.chat.title} ❖━ 
╭════•┈┈┈┈•════╮  
┃ ✦ 𝙽𝚊𝚖𝚎: {user.mention}  
┃ ✦ 𝚄𝚜𝚎𝚛𝚗𝚊𝚖𝚎: @{user.username or "No Username"}  
┃ ✦ 𝙸𝙳: {user.id}  
┃ ✦ 𝚃𝚘𝚝𝚊𝚕 𝙼𝚎𝚖𝚋𝚎𝚛𝚜: {count}  
╰════•┈┈┈┈•════╯
⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆  
⟡ 𝓜𝓪𝔂 𝔂𝓸𝓾𝓻 𝓳𝓸𝓾𝓻𝓷𝓮𝔂 𝓫𝓮 𝓵𝓾𝓶𝓲𝓷𝓸𝓾𝓼  
⟡ 𝓢𝓱𝓪𝓻𝓮 𝔂𝓸𝓾𝓻 𝓵𝓲𝓰𝓱𝓽 𝔀𝓱𝓮𝓷 𝔂𝓸𝓾'𝓻𝓮 𝓻𝓮𝓪𝓭𝔂
""",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(button_text, url=deep_link)],
                    [InlineKeyboardButton(add_button_text, url=add_link)],
                ])
            )
            temp.MELCOW[f"welcome-{chat_id}"] = welcome_message

            if pic_path and os.path.exists(pic_path) and "AnonXMusic/assets/upic.png" not in pic_path:
                os.remove(pic_path)
            if welcome_img and os.path.exists(welcome_img):
                os.remove(welcome_img)

        except Exception as e:
            LOGGER.error(f"Error in greeting new member: {e}")