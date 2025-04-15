from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app


@app.on_message(filters.command("report") & filters.group)
async def report_handler(client, message: Message):
    chat_id = message.chat.id
    reporter = message.from_user
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."

    if message.reply_to_message:
        reported_msg = message.reply_to_message
        reported_user = reported_msg.from_user
    else:
        reported_msg = message
        reported_user = reporter

    # Fetch group admins
    admins = await client.get_chat_members(chat_id, filter="administrators")
    forwarded_count = 0

    for admin in admins:
        if admin.user.is_bot:
            continue
        try:
            # Forward the reported message to each admin privately
            await client.forward_messages(admin.user.id, chat_id, reported_msg.id)
            await client.send_message(
                admin.user.id,
                f"⚠️ New Report\n"
                f"Group: {message.chat.title}\n"
                f"Reported User: {reported_user.mention}\n"
                f"By: {reporter.mention}\n"
                f"Reason: {reason}"
            )
            forwarded_count += 1
        except Exception:
            pass  # Admin probably hasn't started bot

    # Group message with button
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📬 Report Sent to Admins", callback_data="noop")]]
    )
    await message.reply("⚠️ Report sent to admins via private message.", reply_markup=keyboard)