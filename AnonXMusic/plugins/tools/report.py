from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app


@app.on_message(filters.command("report") & filters.group)
async def report_user(client, message: Message):
    chat_id = message.chat.id
    reporter = message.from_user

    if message.reply_to_message:
        reported_user = message.reply_to_message.from_user
        reported_msg_id = message.reply_to_message.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."
    else:
        reported_user = reporter
        reported_msg_id = message.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."

    # Invisible character (U+2063) hides @admin in text
    invisible = "\u2063"

    # Add @admin after invisible character to ping admins without showing it
    hidden_admin_tag = f"{invisible}@admin"

    report_text = (
        f"⚠️ Report Alert\n\n"
        f"Reported User: {reported_user.mention}\n"
        f"Reported By: {reporter.mention}\n"
        f"Reason: {reason}\n"
        f"{hidden_admin_tag}"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔗 Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{reported_msg_id}")]]
    )

    await message.reply(report_text, reply_markup=keyboard)