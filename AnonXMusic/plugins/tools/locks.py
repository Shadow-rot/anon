from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from AnonXMusic import app

locked_content = {}

ALL_LOCK_TYPES = [
    "text", "photo", "video", "sticker", "voice", "document", "audio", "animation",
    "contact", "poll", "location", "game", "forwarded", "url", "mention", "caption"
]

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@app.on_message(filters.command("locktypes") & filters.group)
async def show_locktypes(client, message: Message):
    types_list = "\n".join(f"- {lock_type}" for lock_type in ALL_LOCK_TYPES)
    await message.reply(f"available lock types:\n{types_list}")

@app.on_message(filters.command("lock") & filters.group)
async def lock_command(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("you must be admin to lock things.")

    if len(message.command) < 2:
        return await message.reply("usage: /lock <type>\nsee /locktypes for all types.")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set(ALL_LOCK_TYPES)
        return await message.reply("all content types have been locked.")

    if lock_type not in ALL_LOCK_TYPES:
        return await message.reply("invalid type. use /locktypes to see valid options.")

    locked_content.setdefault(chat_id, set()).add(lock_type)
    await message.reply(f"{lock_type} locked in this group.")

@app.on_message(filters.command("unlock") & filters.group)
async def unlock_command(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("you must be admin to unlock things.")

    if len(message.command) < 2:
        return await message.reply("usage: /unlock <type>")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set()
        return await message.reply("all content types have been unlocked.")

    if lock_type in locked_content.get(chat_id, set()):
        locked_content[chat_id].remove(lock_type)
        await message.reply(f"{lock_type} unlocked.")
    else:
        await message.reply("this content is not locked.")

@app.on_message(filters.command("locks") & filters.group)
async def list_locks(client, message: Message):
    chat_id = message.chat.id
    locks = locked_content.get(chat_id, set())

    if not locks:
        return await message.reply("no content is locked in this group.")
    
    locked_list = "\n".join(f"- {lock}" for lock in sorted(locks))
    await message.reply(f"currently locked:\n{locked_list}")

@app.on_message(filters.group, group=69)
async def enforce_locks(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    locked = locked_content.get(chat_id, set())

    if not locked:
        return

    # allow admins and owner
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except:
        pass

    # delete message if content type is locked
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
    if "animation" in locked and message.animation:
        return await message.delete()
    if "contact" in locked and message.contact:
        return await message.delete()
    if "poll" in locked and message.poll:
        return await message.delete()
    if "location" in locked and message.location:
        return await message.delete()
    if "game" in locked and message.game:
        return await message.delete()
    if "forwarded" in locked and message.forward_from:
        return await message.delete()
    if "mention" in locked and message.entities:
        if any(ent.type == "mention" for ent in message.entities):
            return await message.delete()
    if "url" in locked and message.entities:
        if any(ent.type == "url" for ent in message.entities):
            return await message.delete()
    if "caption" in locked and message.caption:
        return await message.delete()