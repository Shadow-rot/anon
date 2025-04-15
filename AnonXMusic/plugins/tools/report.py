from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from AnonXMusic import app


@app.on_message(filters.command("report") & filters.group)
async def report_user(client, message: Message):
    chat_id = message.chat.id
    reporter = message.from_user

    # Get reported user and reason
    if message.reply_to_message:
        reported_user = message.reply_to_message.from_user
        reported_msg_id = message.reply_to_message.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."
    else:
        reported_user = reporter
        reported_msg_id = message.id
        reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."

    # Fetch admins and build hidden mentions
    hidden_mentions = ""
    async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        user = member.user
        if not user.is_bot:
            hidden_mentions += f"[‌](tg://user?id={user.id})"  # invisible char: U+200C

    # Build visible report message
    text = (
        "⚠️ Report Alert\n\n"
        f"Reported User: {reported_user.mention}\n"
        f"Reported By: {reporter.mention}\n"
        f"Reason: {reason}\n\n"
        f"{hidden_mentions}"
    )

    # Add button linking to the reported message
    button = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🔗 Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{reported_msg_id}")
        ]]
    )

    await message.reply(text, reply_markup=button, disable_web_page_preview=True)