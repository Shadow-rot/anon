from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from AnonXMusic import app

locked_content = {}

ALL_LOCK_TYPES = [
    "all", "audio", "bots", "button", "contact", "document", "egame", "forward", "game",
    "gif", "info", "inline", "invite", "location", "media", "messages", "other", "photo",
    "pin", "poll", "previews", "rtl", "sticker", "url", "video", "voice"
]

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@app.on_message(filters.command("locktypes") & filters.group)
async def show_locktypes(client, message: Message):
    types_list = "\n".join(f"• {lock_type}" for lock_type in ALL_LOCK_TYPES)
    await message.reply(f"ʟᴏᴄᴋs ᴀᴠᴀɪʟᴀʙʟᴇ:\n{types_list}")

@app.on_message(filters.command("lock") & filters.group)
async def lock_command(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ʟᴏᴄᴋ ᴛʜɪɴɢs.")

    if len(message.command) < 2:
        return await message.reply("usage: /lock <type>\nsee /locktypes ғᴏʀ ᴀʟʟ ᴛʏᴘᴇs.")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set(ALL_LOCK_TYPES) - {"all"}
        return await message.reply("ʟᴏᴄᴋᴇᴅ ᴀʟʟ.....")

    if lock_type not in ALL_LOCK_TYPES:
        return await message.reply("ɪɴᴠᴀʟɪᴅ ᴛʏᴘᴇ. ᴜsᴇ /locktypes ᴛᴏ sᴇᴇ ᴠᴀʟɪᴅ ʟᴏᴄᴋ.")

    locked_content.setdefault(chat_id, set()).add(lock_type)
    await message.reply(f"{lock_type} ʟᴏᴄᴋᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")

@app.on_message(filters.command("unlock") & filters.group)
async def unlock_command(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴜɴʟᴏᴄᴋ ʟᴏᴄᴋs.")

    if len(message.command) < 2:
        return await message.reply("usage: /unlock <type>")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set()
        return await message.reply("ᴜɴʟᴏᴋᴇᴅ ᴀʟʟ...
.")

    if lock_type in locked_content.get(chat_id, set()):
        locked_content[chat_id].remove(lock_type)
        await message.reply(f"{lock_type} unlocked.")
    else:
        await message.reply("ᴛʜɪs ᴄᴏɴᴛᴇɴᴛ ɪs ɴᴏᴛ ʟᴏᴄᴋᴇᴅ.")

@app.on_message(filters.command("locks") & filters.group)
async def list_locks(client, message: Message):
    chat_id = message.chat.id
    locks = locked_content.get(chat_id, set())

    if not locks:
        return await message.reply("ɴᴏᴛʜɪɴɢ ʟᴏᴄᴋᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜ ɴᴏᴡ.")
    
    locked_list = "\n".join(f"• {lock}" for lock in sorted(locks))
    await message.reply(f"ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ:\n{locked_list}")

@app.on_message(filters.group, group=69)
async def enforce_locks(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    locks = locked_content.get(chat_id, set())

    if not locks:
        return

    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except:
        pass

    # Lock logic for non-admins
    if "messages" in locks:
        return await message.delete()
    if "text" in locks and message.text:
        return await message.delete()
    if "photo" in locks and message.photo:
        return await message.delete()
    if "video" in locks and message.video:
        return await message.delete()
    if "sticker" in locks and message.sticker:
        return await message.delete()
    if "voice" in locks and message.voice:
        return await message.delete()
    if "audio" in locks and message.audio:
        return await message.delete()
    if "document" in locks and message.document:
        return await message.delete()
    if "animation" in locks and message.animation:
        return await message.delete()
    if "contact" in locks and message.contact:
        return await message.delete()
    if "poll" in locks and message.poll:
        return await message.delete()
    if "location" in locks and message.location:
        return await message.delete()
    if "game" in locks or "egame" in locks and message.game:
        return await message.delete()
    if "forward" in locks and message.forward_from:
        return await message.delete()
    if "bots" in locks and message.from_user.is_bot:
        return await message.delete()
    if "url" in locks and message.entities:
        if any(e.type == "url" for e in message.entities):
            return await message.delete()
    if "mention" in locks and message.entities:
        if any(e.type == "mention" for e in message.entities):
            return await message.delete()
    if "caption" in locks and message.caption:
        return await message.delete()
    if "pin" in locks and message.pinned_message:
        return await message.delete()
    if "inline" in locks and message.via_bot:
        return await message.delete()
    if "previews" in locks and message.web_page:
        return await message.delete()
    if "rtl" in locks and message.text and any("\u202E" in message.text for c in message.text):
        return await message.delete()
    if "media" in locks and (message.media or message.photo or message.video or message.document or message.audio):
        return await message.delete()
    if "other" in locks and not any([
        message.text, message.photo, message.video, message.sticker, message.voice,
        message.document, message.audio, message.animation, message.contact,
        message.poll, message.location, message.game
    ]):
        return await message.delete()