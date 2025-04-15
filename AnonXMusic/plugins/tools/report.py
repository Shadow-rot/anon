from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app


@app.on_message(filters.command("report") & filters.group)
async def report_user(client, message: Message):
    chat_id = message.chat.id
    reporter = message.from_user

    # Check if command was in reply to a message
    if message.reply_to_message:
        reported_user = message.reply_to_message.from_user
        reported_msg_id = message.reply_to_message.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."
    else:
        reported_user = reporter
        reported_msg_id = message.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."

    # Main report message
    report_text = (
        "⚠️ Report Sent\n\n"
        f"Reported User: {reported_user.mention}\n"
        f"Reported By: {reporter.mention}\n"
        f"Reason: {reason}"
    )

    # This message will notify all admins like native @admin
    await message.reply(
        report_text + "\n@admin",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔗 Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{reported_msg_id}")]
            ]
        )
    )