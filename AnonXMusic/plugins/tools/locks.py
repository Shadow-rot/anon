from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

# In-memory storage for locked content types
locked_content = {}

# /lock command
@app.on_message(filters.command("lock") & filters.group & admin_filter)
async def lock_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/lock <type>`\nTypes: text, photo, video, sticker, voice, document, audio")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    locked_content.setdefault(chat_id, set()).add(lock_type)
    await message.reply(f"**Locked `{lock_type}` content in this group.**")

# /unlock command
@app.on_message(filters.command("unlock") & filters.group & admin_filter)
async def unlock_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/unlock <type>`")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type in locked_content.get(chat_id, set()):
        locked_content[chat_id].remove(lock_type)
        await message.reply(f"**Unlocked `{lock_type}` content.**")
    else:
        await message.reply("**This content is not currently locked.**")

# Block locked messages (handler)
@app.on_message(filters.group, group=69)
async def enforce_locks(client, message: Message):
    chat_id = message.chat.id
    locked = locked_content.get(chat_id, set())

    # Check locked types and delete if matched
    if "text" in locked and message.text and not message.via_bot and not message.reply_to_message:
        return await message.delete()
    if "photo" in locked and message.photo:
        return await message.delete()
    if "video" in locked and message.video:
        return await message.delete()
    if "sticker" in locked and message.sticker:
        return await message.delete()
    if "voice" in locked and message.voice:
        return await message.delete()
    if "audio" in locked and message.audio:
        return await message.delete()
    if "document" in locked and message.document:
        return await message.delete()