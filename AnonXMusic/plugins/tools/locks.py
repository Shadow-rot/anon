from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from AnonXMusic import app

locked_content = {}

ALL_LOCK_TYPES = [
    "audio", "bots", "button", "contact", "document", "egame", "forward", "game",
    "gif", "info", "inline", "invite", "location", "media", "messages", "other",
    "photo", "pin", "poll", "previews", "rtl", "sticker", "url", "video", "voice",
    "mention", "caption", "text", "animation"
]

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@app.on_message(filters.command("locktypes") & filters.group)
async def show_locktypes(client, message: Message):
    types_list = "\n".join(f"• {lock_type}" for lock_type in sorted(ALL_LOCK_TYPES))
    await message.reply(f"Available lock types:\n{types_list}")

@app.on_message(filters.command("lock") & filters.group)
async def lock_command(client, message: Message):
    if not message.from_user or not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("You must be an admin to lock things.")

    if len(message.command) < 2:
        return await message.reply("Usage: /lock <type>\nUse /locktypes to see all valid types.")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set(ALL_LOCK_TYPES)
        return await message.reply("✅ All content types have been locked in this group.")

    if lock_type not in ALL_LOCK_TYPES:
        return await message.reply("Invalid type. Use /locktypes to see valid locks.")

    locked_content.setdefault(chat_id, set()).add(lock_type)
    await message.reply(f"✅ Locked: {lock_type}")

@app.on_message(filters.command("unlock") & filters.group)
async def unlock_command(client, message: Message):
    if not message.from_user or not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("You must be an admin to unlock things.")

    if len(message.command) < 2:
        return await message.reply("Usage: /unlock <type>")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set()
        return await message.reply("✅ All content has been unlocked.")

    if lock_type in locked_content.get(chat_id, set()):
        locked_content[chat_id].remove(lock_type)
        await message.reply(f"✅ Unlocked: {lock_type}")
    else:
        await message.reply("That type is not currently locked.")

@app.on_message(filters.command("locks") & filters.group)
async def list_locks(client, message: Message):
    chat_id = message.chat.id
    locks = locked_content.get(chat_id, set())

    if not locks:
        return await message.reply("No locks are active in this group.")

    locked_list = "\n".join(f"• {lock}" for lock in sorted(locks))
    await message.reply(f"Currently locked:\n{locked_list}")

@app.on_message(filters.group)
async def enforce_locks(client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    locks = locked_content.get(chat_id, set())

    if not locks or await is_admin(client, chat_id, user_id):
        return

    try:
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
        if ("game" in locks or "egame" in locks) and message.game:
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
        if "rtl" in locks and message.text and "\u202E" in message.text:
            return await message.delete()
        if "media" in locks and (message.photo or message.video or message.document or message.audio):
            return await message.delete()
        if "other" in locks and not any([
            message.text, message.photo, message.video, message.sticker, message.voice,
            message.document, message.audio, message.animation, message.contact,
            message.poll, message.location, message.game
        ]):
            return await message.delete()
    except Exception as e:
        print(f"[LOCK ENFORCE ERROR]: {e}")