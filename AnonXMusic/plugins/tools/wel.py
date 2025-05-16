"""
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app
from config import MONGO_DB_URI
from pymongo import MongoClient

# MongoDB Setup
client = MongoClient(MONGO_DB_URI)
db = client["anonx_welcome"]
col = db["welcome_data"]

# Helper: Parse buttons
def parse_buttons(button_text):
    lines = button_text.split('\n')
    buttons = []
    for line in lines:
        parts = line.strip().split(" - ")
        if len(parts) == 2:
            label, url = parts
            buttons.append([InlineKeyboardButton(text=label.strip(), url=url.strip())])
    return InlineKeyboardMarkup(buttons) if buttons else None

# Set Welcome Message
@app.on_message(filters.command("setwelcome") & filters.group)
async def set_welcome(_, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a media or text message to set it as the welcome message!")

    buttons = None
    if len(message.command) > 1:
        button_text = message.text.split(None, 1)[1]
        buttons = parse_buttons(button_text)

    media_id = None
    media_type = None

    if message.reply_to_message.photo:
        media_id = message.reply_to_message.photo.file_id
        media_type = "photo"
    elif message.reply_to_message.video:
        media_id = message.reply_to_message.video.file_id
        media_type = "video"
    elif message.reply_to_message.text:
        media_text = message.reply_to_message.text
    else:
        return await message.reply("Unsupported media type.")

    col.update_one(
        {"chat_id": message.chat.id},
        {"$set": {
            "media_id": media_id,
            "media_type": media_type,
            "media_text": message.reply_to_message.text or None,
            "buttons": message.text.split(None, 1)[1] if len(message.command) > 1 else None
        }},
        upsert=True
    )
    await message.reply("Welcome message has been set successfully!")

# Delete Welcome
@app.on_message(filters.command("delwelcome") & filters.group)
async def delete_welcome(_, message: Message):
    col.delete_one({"chat_id": message.chat.id})
    await message.reply("Welcome message deleted.")

# Show Welcome Settings
@app.on_message(filters.command("welcome") & filters.group)
async def show_welcome(_, message: Message):
    data = col.find_one({"chat_id": message.chat.id})
    if not data:
        return await message.reply("No welcome message set.")
    msg = f"**Welcome Settings:**\n"
    msg += f"Type: {data.get('media_type') or 'text'}\n"
    if data.get('buttons'):
        msg += f"Buttons: Yes"
    await message.reply(msg)

# Send Welcome on Join
@app.on_message(filters.new_chat_members)
async def welcome_new_member(_, message: Message):
    data = col.find_one({"chat_id": message.chat.id})
    if not data:
        return

    user_mention = message.new_chat_members[0].mention
    buttons = parse_buttons(data.get("buttons", "")) if data.get("buttons") else None

    caption = data.get("media_text", "").replace("{mention}", user_mention)

    if data.get("media_type") == "photo":
        await message.reply_photo(
            data["media_id"],
            caption=caption or f"Welcome {user_mention}!",
            reply_markup=buttons
        )
    elif data.get("media_type") == "video":
        await message.reply_video(
            data["media_id"],
            caption=caption or f"Welcome {user_mention}!",
            reply_markup=buttons
        )
    else:
        await message.reply(
            caption or f"Welcome {user_mention}!",
            reply_markup=buttons
        )

# Help Message
@app.on_message(filters.command("welcomehelp"))
async def welcome_help(_, message: Message):
    text = """ """
**Welcome Module Help**

Commands:
/setwelcome [optional buttons]
→ Reply to a message (text/photo/video) to set welcome message.
→ Button format:
Button Name - https://example.com

You can use {mention} in your welcome text.

/delwelcome - Delete current welcome message
/welcome - Show current welcome settings
/welcomehelp - Show this help message
    """

    await message.reply(text)
"""
"""