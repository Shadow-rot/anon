import re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient
from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check

# MongoDB Setup
MONGO_URI = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["AnonXMusic"]["welcome"]

# Format placeholders
def format_text(text: str, user, chat):
    return text.format(
        mention=user.mention,
        first_name=user.first_name,
        last_name=user.last_name or "",
        full_name=f"{user.first_name} {(user.last_name or '')}".strip(),
        username=f"@{user.username}" if user.username else user.first_name,
        chat_title=chat.title
    )

# Set welcome
@app.on_message(filters.command("setwelcome") & filters.group)
@admin_check
async def set_welcome(app, message: Message):
    chat_id = message.chat.id

    if not await is_bot_admin(chat_id):
        return await message.reply("🚫 I need to be admin to save welcome messages.")

    if message.reply_to_message:
        content_type = "media" if message.reply_to_message.media else "text"
        msg_id = message.reply_to_message.id
        text = message.reply_to_message.caption or message.reply_to_message.text or "Welcome {mention}"
    elif len(message.command) > 1:
        content_type = "text"
        msg_id = None
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply("📌 Reply to a message or provide text after the command.")

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

# Delete welcome
@app.on_message(filters.command("delwelcome") & filters.group)
@admin_check
async def del_welcome(app, message: Message):
    result = await db.delete_one({"chat_id": message.chat.id})
    if result.deleted_count:
        await message.reply("❌ Welcome message deleted.", parse_mode=ParseMode.HTML)
    else:
        await message.reply("⚠️ No welcome message was set.", parse_mode=ParseMode.HTML)

# Send welcome when member joins
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

# Help module
@app.on_message(filters.command("welcomehelp") & filters.group)
@admin_check
async def welcome_help(app, message: Message):
    help_text = (
        "<b>👋 Welcome System Help</b>\n\n"
        "📌 To set welcome:\n"
        "• <code>/setwelcome Your text here</code>\n"
        "• Or reply to any message (media/text) with <code>/setwelcome</code>\n\n"
        "🧩 Variables:\n"
        "• <code>{mention}</code> - Mention user\n"
        "• <code>{first_name}</code>, <code>{last_name}</code>\n"
        "• <code>{full_name}</code>, <code>{username}</code>\n"
        "• <code>{chat_title}</code> - Group name\n\n"
        "🗑 To delete:\n"
        "<code>/delwelcome</code>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 How to Set", callback_data="help_set"),
         InlineKeyboardButton("🗑 Delete", callback_data="help_del")],
        [InlineKeyboardButton("🧩 Variables", callback_data="help_vars")]
    ])

    await message.reply(help_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Help buttons
@app.on_callback_query(filters.regex("help_"))
async def on_help_button(app, callback):
    data = callback.data

    if data == "help_set":
        await callback.message.edit_text(
            "To set welcome:\n\n"
            "• /setwelcome Welcome {mention} to {chat_title}\n"
            "• Or reply to a media/text with /setwelcome\n\n"
            "Supports buttons and variables.",
            parse_mode=ParseMode.HTML)
    elif data == "help_del":
        await callback.message.edit_text(
            "To delete welcome message:\n\n"
            "<code>/delwelcome</code>",
            parse_mode=ParseMode.HTML)
    elif data == "help_vars":
        await callback.message.edit_text(
            "Available variables:\n\n"
            "• {mention} - User mention\n"
            "• {first_name}, {last_name}\n"
            "• {full_name}, {username}\n"
            "• {chat_title} - Group name",
            parse_mode=ParseMode.HTML)

    await callback.answer()