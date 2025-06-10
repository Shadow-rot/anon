# welcome.py

import re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatPermissions
from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["anonxmusic"]["welcome"]

def parse_variables(text: str, user, chat):
    variables = {
        "{first}": user.first_name or "",
        "{last}": user.last_name or user.first_name or "",
        "{fullname}": f"{user.first_name or ''} {user.last_name or ''}".strip(),
        "{mention}": user.mention,
        "{username}": f"@{user.username}" if user.username else user.mention,
        "{id}": str(user.id),
        "{chatname}": chat.title,
        "{count}": str(chat.members_count) if hasattr(chat, 'members_count') else "N/A",
    }
    for key, value in variables.items():
        text = text.replace(key, value)
    return text


def extract_buttons(text: str):
    pattern = r"(.*?)buttonurl://(.*?)(:same)?"
    matches = re.findall(pattern, text)
    buttons = []
    current_row = []

    for match in matches:
        label, url, same = match
        btn = InlineKeyboardButton(label, url=url)
        if same:
            current_row.append(btn)
        else:
            if current_row:
                buttons.append(current_row)
            current_row = [btn]

    if current_row:
        buttons.append(current_row)

    clean_text = re.sub(pattern, "", text).strip()
    return clean_text, buttons
# Set welcome
@app.on_message(filters.command("setwelcome") & filters.group)
@admin_check
async def set_welcome(_, message: Message):
    chat_id = message.chat.id
    bot_member = await app.get_chat_member(chat_id, "me")

    if not bot_member.can_send_messages:
        return await message.reply("I don't have permission to send messages in this group.")

    reply = message.reply_to_message
    if not reply:
        return await message.reply("Reply to a text/media to set as welcome.")

    file_id = None
    media_type = None
    if reply.photo:
        file_id, media_type = reply.photo.file_id, "photo"
    elif reply.video:
        file_id, media_type = reply.video.file_id, "video"
    elif reply.audio:
        file_id, media_type = reply.audio.file_id, "audio"
    elif reply.voice:
        file_id, media_type = reply.voice.file_id, "voice"
    elif reply.document:
        file_id, media_type = reply.document.file_id, "document"
    elif reply.text:
        media_type = "text"

    raw_text = reply.caption if media_type != "text" else reply.text
    text, buttons = extract_buttons(raw_text or "")

    await db.update_one({"chat_id": chat_id}, {
        "$set": {
            "text": text,
            "media_type": media_type,
            "file_id": file_id,
            "buttons": buttons
        }
    }, upsert=True)

    await message.reply("✅ Welcome message has been set successfully.")

# Delete welcome
@app.on_message(filters.command("delwelcome") & filters.group)
@admin_check
async def delete_welcome(_, message: Message):
    chat_id = message.chat.id
    deleted = await db.delete_one({"chat_id": chat_id})
    if deleted.deleted_count:
        await message.reply("✅ Welcome message deleted.")
    else:
        await message.reply("No welcome message was set.")

@app.on_message(filters.command("welcomehelp"))
async def welcome_help(_, message: Message):
    text = (
        "<b>👋 Welcome Module Help</b>\n\n"
        "<b>Commands:</b>\n"
        "• <code>/setwelcome</code> - Reply to any message or text to set it as welcome.\n"
        "• <code>/delwelcome</code> - Delete current welcome.\n"
        "• <code>/welcomehelp</code> - Show this help.\n\n"
        "<b>Supported Variables:</b>\n"
        "• {first} - First name\n"
        "• {last} - Last name\n"
        "• {fullname} - Full name\n"
        "• {username} - Username or mention\n"
        "• {mention} - Mention\n"
        "• {id} - User ID\n"
        "• {chatname} - Chat title\n"
        "• {count} - Member count\n\n"
        "<b>Formatting:</b>\n"
        "• <code>*bold*</code>, <code>_italic_</code>, <code>__underline__</code>\n"
        "• <code>[text](buttonurl://link)</code> - Button\n"
        "• <code>:same</code> - Add button to same row\n"
        "• Reply with any media to set media-based welcome.\n\n"
        "Example:\n<code>Hello {mention}, welcome to {chatname}!</code>\n"
        "[Rules](buttonurl://t.me/yourruleslink)\n\n"
        "➕ Buttons, Markdown, media all are supported!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Back to Group", url=f"https://t.me/{app.me.username}?startgroup=true")],
    ])

    await message.reply(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

@app.on_message(filters.new_chat_members)
async def welcome_new_member(_, message: Message):
    chat_id = message.chat.id
    data = await db.find_one({"chat_id": chat_id})
    if not data:
        return

    for user in message.new_chat_members:
        text = parse_variables(data.get("text", "Welcome {mention}!"), user, message.chat)
        buttons = InlineKeyboardMarkup(data.get("buttons", [])) if data.get("buttons") else None

        if data["media_type"] == "text":
            await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)
        else:
            send_kwargs = dict(chat_id=chat_id, caption=text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)
            if data["media_type"] == "photo":
                await app.send_photo(data["file_id"], **send_kwargs)
            elif data["media_type"] == "video":
                await app.send_video(data["file_id"], **send_kwargs)
            elif data["media_type"] == "audio":
                await app.send_audio(data["file_id"], **send_kwargs)
            elif data["media_type"] == "voice":
                await app.send_voice(data["file_id"], **send_kwargs)
            elif data["media_type"] == "document":
                await app.send_document(data["file_id"], **send_kwargs)