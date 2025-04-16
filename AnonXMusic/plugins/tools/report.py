"""from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from AnonXMusic import app
from pyrogram.errors import PeerIdInvalid, UserIsBlocked

# Report command handler
@app.on_message(filters.command("report") & filters.group)
async def report_handler(client, message):
    # Ensure the message is a reply
    if not message.reply_to_message:
        return await message.reply("Please reply to a message to report.")

    reporter = message.from_user
    reported_message = message.reply_to_message
    reported_user = reported_message.from_user

    # Ensure you're not reporting yourself
    if not reported_user or reported_user.id == reporter.id:
        return

    # Build the report text
    chat = message.chat
    chat_name = chat.title or "this group"
    report_text = (
        f"⚠️ <b>Report from:</b> {reporter.mention}\n"
        f"<b>Group:</b> {chat_name}\n"
        f"<b>Reported:</b> {reported_user.mention}\n"
        f"<b>Reason:</b> {' '.join(message.command[1:]) or 'No reason provided'}"
    )

    # Inline buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡ View Message", url=f"https://t.me/{chat.username}/{reported_message.id}")
         ] if chat.username else []],
        [
            InlineKeyboardButton("⚠ Kick", callback_data=f"report_kick_{chat.id}_{reported_user.id}"),
            InlineKeyboardButton("⛔ Ban", callback_data=f"report_ban_{chat.id}_{reported_user.id}")
        ],
        [InlineKeyboardButton("❌ Delete", callback_data=f"report_del_{chat.id}_{reported_message.id}")]
    ])

    # Notify all admins
    async for member in client.get_chat_members(chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        admin = member.user
        if admin.is_bot:
            continue
        try:
            await client.send_message(admin.id, report_text, reply_markup=buttons, parse_mode="html")
            await reported_message.forward(admin.id)
        except (PeerIdInvalid, UserIsBlocked):
            continue

    await message.reply("✅ Report sent to admins.")


# Callback query handler for admin actions (Kick, Ban, Delete)
@app.on_callback_query(filters.regex(r"^report_(kick|ban|del)_(\d+)_(\d+)$"))
async def report_button_handler(client, callback_query: CallbackQuery):
    action, chat_id, target_id = callback_query.data.split("_")[1:]

    try:
        if action == "kick":
            await client.ban_chat_member(int(chat_id), int(target_id))
            await client.unban_chat_member(int(chat_id), int(target_id))
            await callback_query.answer("User kicked.")
        elif action == "ban":
            await client.ban_chat_member(int(chat_id), int(target_id))
            await callback_query.answer("User banned.")
        elif action == "del":
            await client.delete_messages(int(chat_id), int(target_id))
            await callback_query.answer("Message deleted.")
    except Exception as e:
        await callback_query.answer("Action failed.")
        print(f"[REPORT ERROR] {e}")


# Optionally: Add toggles for report preferences (chat-based or user-based)
# These functions would interact with your SQL or config database to enable/disable reporting per user or group.

# Example function to toggle report settings
@app.on_message(filters.command("reports") & filters.group)
async def report_setting(client, message):
    args = message.command[1:]
    chat = message.chat

    if len(args) >= 1:
        if args[0] in ("yes", "on"):
            # SQL logic: Enable reporting for the chat
            sql.set_chat_setting(chat.id, True)
            await message.reply("Report system enabled for this group.")
        elif args[0] in ("no", "off"):
            # SQL logic: Disable reporting for the chat
            sql.set_chat_setting(chat.id, False)
            await message.reply("Report system disabled for this group.")
        else:
            await message.reply("Usage: /reports <on/off>")
    else:
        # Check current setting (using SQL or a config method)
        current_setting = sql.chat_should_report(chat.id)
        await message.reply(f"Reporting is currently {'enabled' if current_setting else 'disabled'}.")
"""