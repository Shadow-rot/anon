from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from AnonXMusic import app
from AnonXMusic.utils.autofix import auto_fix_handler

@app.on_message(filters.command("id"))
@auto_fix_handler
async def id_handler(client, message: Message):
    reply = message.reply_to_message
    args = message.text.split(maxsplit=1)

    # Case 1: Reply to someone
    if reply and reply.from_user:
        user = reply.from_user
        return await message.reply_text(
            f"User: <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
            f"User ID:\n<code>{user.id}</code>",
            parse_mode=ParseMode.HTML
        )

    # Case 2: Argument with username
    if len(args) > 1:
        username = args[1].strip().replace("@", "")
        try:
            user = await client.get_users(username)
            return await message.reply_text(
                f"User: <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
                f"User ID:\n<code>{user.id}</code>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            return await message.reply_text(f"❌ Failed to fetch user: {e}")

    # Case 3: Default (no reply, no argument)
    user = message.from_user
    chat = message.chat
    text = (
        f"You: <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
        f"Your ID:\n<code>{user.id}</code>\n"
        f"Chat ID:\n<code>{chat.id}</code>"
    )
    await message.reply_text(text, parse_mode=ParseMode.HTML)