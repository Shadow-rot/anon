from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app

@app.on_message(filters.command("id"))
async def id_handler(client, message: Message):
    reply = message.reply_to_message

    if reply and reply.from_user:
        user = reply.from_user
        return await message.reply_text(
            f"User: {user.mention}\nID: `{user.id}`"
        )

    user = message.from_user
    chat = message.chat

    text = (
        f"You: {user.mention}\n"
        f"Your ID: ` {user.id} `\n"
        f"Chat ID: ` {chat.id} `"
    )
    await message.reply_text(text)