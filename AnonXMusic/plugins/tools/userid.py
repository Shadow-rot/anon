from datetime import datetime
from pyrogram import filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message
from AnonXMusic import app

@app.on_message(filters.command("id"))
async def get_ids(client, message: Message):
    reply = message.reply_to_message
    text = ""

    chat = message.chat
    from_user = message.from_user

    # Message and user info
    text += f"Message ID: {message.id}\n"
    if from_user:
        text += f"Your ID: {from_user.id} (tg://user?id={from_user.id})\n"
        text += f"Is Bot: {from_user.is_bot}\n"

    # Chat Info
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        chat_link = f"https://t.me/{chat.username}" if chat.username else "Private"
        text += f"Chat ID: {chat.id}\n"
        text += f"Chat Title: {chat.title}\n"
        text += f"Chat Link: {chat_link}\n"

    elif chat.type == ChatType.PRIVATE:
        text += f"Private Chat ID: {chat.id}\n"

    # Replied Message Info
    if reply:
        if reply.from_user:
            user = reply.from_user
            text += "\nReplied Message:\n"
            text += f"Name: {user.first_name}\n"
            text += f"ID: {user.id}\n"
            if user.username:
                text += f"Username: @{user.username}\n"
            text += f"Bot: {user.is_bot}\n"
            text += f"Replied Message ID: {reply.id}\n"

        if reply.forward_from:
            fwd_user = reply.forward_from
            text += "\nForwarded From User:\n"
            text += f"Name: {fwd_user.first_name}\n"
            text += f"ID: {fwd_user.id}\n"
            if fwd_user.username:
                text += f"Username: @{fwd_user.username}\n"

        elif reply.forward_from_chat:
            fwd_chat = reply.forward_from_chat
            text += "\nForwarded From Channel/Group:\n"
            text += f"Title: {fwd_chat.title}\n"
            text += f"ID: {fwd_chat.id}\n"
            if fwd_chat.username:
                text += f"Username: @{fwd_chat.username}\n"

        if reply.sender_chat:
            sender = reply.sender_chat
            text += "\nSender Chat (Anonymous Admin / Channel):\n"
            text += f"Title: {sender.title}\n"
            text += f"ID: {sender.id}\n"

    # Optional: Check target from command
    if len(message.command) > 1:
        target = message.text.split(None, 1)[1]
        try:
            user = await client.get_users(target)
            text += "\nTarget User from Command:\n"
            text += f"Name: {user.first_name}\n"
            text += f"ID: {user.id}\n"
            if user.username:
                text += f"Username: @{user.username}\n"
            text += f"Bot: {user.is_bot}\n"
        except Exception:
            text += f"\nFailed to fetch user '{target}'."

    # Timestamp
    text += f"\nTimestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"

    await message.reply_text(text, parse_mode=ParseMode.DEFAULT, disable_web_page_preview=True)