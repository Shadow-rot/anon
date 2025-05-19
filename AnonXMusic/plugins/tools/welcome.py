import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from logging import getLogger
from AnonXMusic import app


LOGGER = getLogger(__name__)


# In-memory welcome state store
class WelcomeState:
    def __init__(self):
        self.data = {}
        self.auto_disabled = {}
        self.joins = {}
        self.timestamps = {}

    async def get(self, chat_id):
        return self.data.get(chat_id, "on")

    async def set(self, chat_id, state):
        self.data[chat_id] = state

    async def is_on(self, chat_id):
        return await self.get(chat_id) == "on"

    async def track_join(self, chat_id):
        now = datetime.now(timezone.utc)
        last = self.timestamps.get(chat_id, now)
        if (now - last).total_seconds() > 8:
            self.joins[chat_id] = 1
        else:
            self.joins[chat_id] = self.joins.get(chat_id, 0) + 1
        self.timestamps[chat_id] = now
        return self.joins[chat_id]

    async def auto_disable(self, chat_id):
        await self.set(chat_id, "off")
        self.auto_disabled[chat_id] = datetime.now(timezone.utc) + timedelta(minutes=30)

    async def auto_reenable(self, chat_id):
        t = self.auto_disabled.get(chat_id)
        if t and datetime.now(timezone.utc) >= t:
            await self.set(chat_id, "on")
            del self.auto_disabled[chat_id]
            return True
        return False


state = WelcomeState()
temp_msg = {}

# Mask profile picture to circle
def make_circle(image, size=(500, 500)):
    image = image.resize(size).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    image.putalpha(mask)
    return image


# Compose final welcome image
def create_welcome_image(profile_path, name, user_id, username):
    bg = Image.open("/mnt/data/file-PRsPtTMYFwsb8EBdbPUex6").convert("RGBA")
    font = ImageFont.truetype("AnonXMusic/assets/ArialReg.ttf", 65)

    draw = ImageDraw.Draw(bg)

    def draw_center(text, y):
        w, _ = draw.textsize(text, font=font)
        draw.text(((bg.width - w) / 2, y), text, font=font, fill=(255, 255, 255))

    draw_center(name, 715)
    draw_center(str(user_id), 1005)
    draw_center(username, 1308)

    pfp = Image.open(profile_path).convert("RGBA")
    pfp = make_circle(pfp, (500, 500))
    bg.paste(pfp, (715, 390), pfp)

    output = f"downloads/wel_{user_id}.png"
    bg.save(output)
    return output


@app.on_message(filters.command("wel") & filters.group)
async def toggle_welcome(app, message):
    if len(message.command) != 2:
        return await message.reply("Usage: `/wel on` or `/wel off`")

    status = message.command[1].lower()
    if status not in ["on", "off"]:
        return await message.reply("Choose `on` or `off`.")

    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply("You must be an admin.")

    await state.set(message.chat.id, status)
    await message.reply(f"Welcome system turned `{status}`.")


@app.on_chat_member_updated(filters.group, group=-3)
async def welcome_user(app, member: ChatMemberUpdated):
    chat_id = member.chat.id
    user = member.new_chat_member.user

    if not member.new_chat_member or member.new_chat_member.status != enums.ChatMemberStatus.MEMBER:
        return

    if not await state.is_on(chat_id):
        if await state.auto_reenable(chat_id):
            await app.send_message(chat_id, "Welcome messages re-enabled.")
        else:
            return

    if await state.track_join(chat_id) >= 10:
        await state.auto_disable(chat_id)
        await app.send_message(chat_id, "Join flood detected. Welcome messages disabled for 30 mins.")
        return

    try:
        pic = "AnonXMusic/assets/upic.png"
        photos = await app.get_profile_photos(user.id, limit=1)
        if photos:
            pic = await app.download_media(photos[0].file_id, file_name=f"downloads/pp{user.id}.png")

        if temp_msg.get(chat_id):
            try:
                await temp_msg[chat_id].delete()
            except:
                pass

        img = create_welcome_image(
            pic, user.first_name, user.id, f"@{user.username}" if user.username else "No Username"
        )

        count = await app.get_chat_members_count(chat_id)
        welcome = await app.send_photo(
            chat_id,
            photo=img,
            caption=f"""
✦ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {member.chat.title} ✦

➥ Name: {user.mention}
➥ ID: {user.id}
➥ Username: @{user.username or "None"}
➥ Total Members: {count}
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("๏ Profile ๏", url=f"tg://user?id={user.id}")],
                [InlineKeyboardButton("๏ Invite Bot ๏", url=f"https://t.me/{app.me.username}?startgroup=true")]
            ])
        )
        temp_msg[chat_id] = welcome

        if "pp" in pic and os.path.exists(pic):
            os.remove(pic)
        if os.path.exists(img):
            os.remove(img)

    except Exception as e:
        LOGGER.error(f"Error in welcome message: {e}")


if __name__ == "__main__":
    app.run()