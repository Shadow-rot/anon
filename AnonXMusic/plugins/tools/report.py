from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from AnonXMusic import app

# /report command
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

    report_text = (
        "⚠️ Report Alert\n\n"
        f"Reported User: {reported_user.mention}\n"
        f"Reported By: {reporter.mention}\n"
        f"Reason: {reason}"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Notify Admins", callback_data=f"notify_admins_{chat_id}")],
         [InlineKeyboardButton("🔗 Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{reported_msg_id}")]]
    )

    await message.reply(report_text, reply_markup=keyboard)

# Button handler to notify admins silently
@app.on_callback_query(filters.regex("^notify_admins_"))
async def notify_admins(client, callback_query: CallbackQuery):
    chat_id = int(callback_query.data.split("_")[2])

    # Create invisible mention tags for all admins
    hidden_mentions = ""
    async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if not member.user.is_bot:
            hidden_mentions += f"[‎](tg://user?id={member.user.id})"  # Invisible char + hidden mention

    await callback_query.answer("Admins have been silently notified.", show_alert=False)
    await client.send_message(chat_id, hidden_mentions)