import re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from AnonXMusic import app

# MongoDB Setup
MONGO_URI = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["AnonXMusic"]["welcome"]

# Text Formatter
def format_text(text: str, user, chat):
    return text.format(
        mention=user.mention,
        first_name=user.first_name,
        last_name=user.last_name or "",
        full_name=f"{user.first_name} {(user.last_name or '')}".strip(),
        username=f"@{user.username}" if user.username else user.first_name,
        chat_title=chat.title
    )

# /setwelcome
@app.on_message(filters.command("setwelcome") & filters.group)
async def set_welcome(app, message: Message):
    chat_id = message.chat.id

    if message.reply_to_message:
        content_type = "media" if message.reply_to_message.media else "text"
        msg_id = message.reply_to_message.id
        text = message.reply_to_message.caption or message.reply_to_message.text or "Welcome {mention}"
    elif len(message.command) > 1:
        content_type = "text"
        msg_id = None
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply("Reply to a message or provide welcome text after the command.")

    reply_markup = message.reply_to_message.reply_markup if message.reply_to_message else None
    buttons = []
    if reply_markup:
        for row in reply_markup.inline_keyboard:
            for btn in row:
                if btn.url:
                    buttons.append([btn.text, btn.url])

    await db.update_one(
        {"chat_id": chat_id},
        {"$set": {
            "type": content_type,
            "msg_id": msg_id,
            "text": text,
            "buttons": buttons
        }},
        upsert=True
    )
    await message.reply("✅ Welcome message saved!", parse_mode=ParseMode.HTML)

# /delwelcome
@app.on_message(filters.command("delwelcome") & filters.group)
async def del_welcome(app, message: Message):
    result = await db.delete_one({"chat_id": message.chat.id})
    if result.deleted_count:
        await message.reply("❌ Welcome message deleted.", parse_mode=ParseMode.HTML)
    else:
        await message.reply("No welcome message found.", parse_mode=ParseMode.HTML)

# Send Welcome
@app.on_message(filters.new_chat_members)
async def welcome_new_member(app, message: Message):
    new_user = message.new_chat_members[0]
    chat_id = message.chat.id

    welcome = await db.find_one({"chat_id": chat_id})
    if not welcome:
        return

    text = format_text(welcome.get("text", "Welcome {mention}"), new_user, message.chat)
    buttons = [[InlineKeyboardButton(text=b[0], url=b[1])] for b in welcome.get("buttons", [])]

    if welcome["type"] == "media" and welcome.get("msg_id"):
        try:
            await app.copy_message(
                chat_id=chat_id,
                from_chat_id=chat_id,
                message_id=welcome["msg_id"],
                caption=text,
                reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
            )
        except Exception:
            await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)
    else:
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)

# /welcomehelp
@app.on_message(filters.command("welcomehelp") & filters.group)
async def welcome_help(app, message: Message):
    help_msg = (
        "<b>Welcome System Help</b>\n\n"
        "Set welcome messages using:\n"
        "➤ <code>/setwelcome Your message here</code>\n"
        "➤ Or reply to a message (with text/media/buttons) with <code>/setwelcome</code>\n\n"
        "Supported variables:\n"
        "• <code>{mention}</code> - Mentions user\n"
        "• <code>{first_name}</code>, <code>{last_name}</code>\n"
        "• <code>{full_name}</code>, <code>{username}</code>\n"
        "• <code>{chat_title}</code> - Group name\n\n"
        "Delete: <code>/delwelcome</code>\n"
        "Try to set via reply with videos, photos, songs etc."
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Set Welcome", callback_data="help_set"),
         InlineKeyboardButton("Delete Welcome", callback_data="help_del")],
        [InlineKeyboardButton("Supported Vars", callback_data="help_vars")]
    ])

    await message.reply(help_msg, reply_markup=buttons, parse_mode=ParseMode.HTML)

# Help Buttons Handler
@app.on_callback_query(filters.regex("help_"))
async def on_help_button(app, callback):
    data = callback.data

    if data == "help_set":
        await callback.message.edit_text(
            "To set welcome:\n• /setwelcome Your text\n• Or reply to a message with /setwelcome\nMedia, buttons, text all supported.",
            parse_mode=ParseMode.HTML)
    elif data == "help_del":
        await callback.message.edit_text(
            "To delete welcome, use:\n• /delwelcome\n\nOnly one welcome message per group is saved.",
            parse_mode=ParseMode.HTML)
    elif data == "help_vars":
        await callback.message.edit_text(
            "Supported Welcome Variables:\n\n"
            "• {mention}\n• {first_name}\n• {last_name}\n• {full_name}\n• {username}\n• {chat_title}",
            parse_mode=ParseMode.HTML)

    await callback.answer()