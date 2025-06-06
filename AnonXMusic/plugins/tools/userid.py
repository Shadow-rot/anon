from datetime import datetime
from pyrogram import filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message
from AnonXMusic import app

@app.on_message(filters.command("id"))
async def get_ids(client, message: Message):
    reply = message.reply_to_message
    chat = message.chat
    from_user = message.from_user

    text = "<b>ID Information:</b>\n\n"

    # Message and sender info
    if from_user:
        text += f"Your Name: {from_user.mention()}\n"
        text += f"Your ID: <code>{from_user.id}</code>\n"
        text += f"Bot: {'Yes' if from_user.is_bot else 'No'}\n"
        text += f"Message ID: <code>{message.id}</code>\n\n"

    # Chat info
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        text += f"Chat Title: {chat.title}\n"
        text += f"Chat ID: <code>{chat.id}</code>\n"
        if chat.username:
            text += f"Chat Username: @{chat.username}\n"
    else:
        text += f"Private Chat ID: <code>{chat.id}</code>\n"

    # Replied message info
    if reply:
        user = reply.from_user or reply.sender_chat
        if user:
            text += "\n<b>Replied Message:</b>\n"
            text += f"From: {user.mention() if hasattr(user, 'mention') else user.title}\n"
            text += f"ID: <code>{user.id}</code>\n"
            text += f"Message ID: <code>{reply.id}</code>\n"

        if reply.forward_from:
            fwd = reply.forward_from
            text += "\n<b>Forwarded From User:</b>\n"
            text += f"Name: {fwd.mention()}\n"
            text += f"ID: <code>{fwd.id}</code>\n"

        elif reply.forward_from_chat:
            fwd_chat = reply.forward_from_chat
            text += "\n<b>Forwarded From Channel/Group:</b>\n"
            text += f"Title: {fwd_chat.title}\n"
            text += f"ID: <code>{fwd_chat.id}</code>\n"
            if fwd_chat.username:
                text += f"Username: @{fwd_chat.username}\n"

        if reply.sender_chat:
            sender = reply.sender_chat
            text += "\n<b>Sender Chat (Anonymous Admin or Channel):</b>\n"
            text += f"Title: {sender.title}\n"
            text += f"ID: <code>{sender.id}</code>\n"

    # Inline user check
    if len(message.command) > 1:
        user_input = message.text.split(None, 1)[1]
        try:
            target = await client.get_users(user_input)
            text += "\n<b>User from Command:</b>\n"
            text += f"Name: {target.mention()}\n"
            text += f"ID: <code>{target.id}</code>\n"
            if target.username:
                text += f"Username: @{target.username}\n"
            text += f"Bot: {'Yes' if target.is_bot else 'No'}\n"
        except Exception:
            text += f"\nCould not find user: <code>{user_input}</code>\n"

    # Timestamp
    text += f"\n<b>Timestamp:</b> <i>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"

    await message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )