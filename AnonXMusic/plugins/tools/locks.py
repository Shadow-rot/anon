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
        return await message.reply("ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ʟᴏᴄᴋ ᴛʜɪɴɢs.")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴀɢᴇ: /lock <ᴛʏᴘᴇ>\nsᴇᴇ /locktypes ꜰᴏʀ ᴀʟʟ ᴛʏᴘᴇs.")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set(ALL_LOCK_TYPES) - {"all"}
        return await message.reply("ʟᴏᴄᴋᴇᴅ ᴀʟʟ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇs.")

    if lock_type not in ALL_LOCK_TYPES:
        return await message.reply("ɪɴᴠᴀʟɪᴅ ᴛʏᴘᴇ. ᴜsᴇ /locktypes ᴛᴏ sᴇᴇ ᴠᴀʟɪᴅ ʟᴏᴄᴋs.")

    locked_content.setdefault(chat_id, set()).add(lock_type)
    await message.reply(f"{lock_type} ʟᴏᴄᴋᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")

@app.on_message(filters.command("unlock") & filters.group)
async def unlock_command(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜɴʟᴏᴄᴋ.")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴀɢᴇ: /unlock <ᴛʏᴘᴇ>")

    lock_type = message.command[1].lower()
    chat_id = message.chat.id

    if lock_type == "all":
        locked_content[chat_id] = set()
        return await message.reply("ᴜɴʟᴏᴄᴋᴇᴅ ᴀʟʟ ᴄᴏɴᴛᴇɴᴛ.")

    if lock_type in locked_content.get(chat_id, set()):
        locked_content[chat_id].remove(lock_type)
        await message.reply(f"{lock_type} ᴜɴʟᴏᴄᴋᴇᴅ.")
    else:
        await message.reply("ᴛʜɪs ᴛʏᴘᴇ ɪs ɴᴏᴛ ʟᴏᴄᴋᴇᴅ.")

@app.on_message(filters.command("locks") & filters.group)
async def list_locks(client, message: Message):
    chat_id = message.chat.id
    locks = locked_content.get(chat_id, set())

    if not locks:
        return await message.reply("ɴᴏᴛʜɪɴɢ ɪs ʟᴏᴄᴋᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")

    locked_list = "\n".join(f"• {lock}" for lock in sorted(locks))
    await message.reply(f"ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ:\n{locked_list}")

@app.on_message(filters.group, group=69)
async def enforce_locks(client, message: Message):
    chat_id = message.chat.id
    from_user = message.from_user

    # Ignore messages with no sender (e.g., anonymous admins or service messages)
    if not from_user:
        return

    user_id = from_user.id
    locks = locked_content.get(chat_id, set())

    # Allow if no locks or user is admin
    if not locks or await is_admin(client, chat_id, user_id):
        return

    # Message type-based deletion
    conditions = [
        ("messages", True),
        ("text", message.text),
        ("photo", message.photo),
        ("video", message.video),
        ("sticker", message.sticker),
        ("voice", message.voice),
        ("audio", message.audio),
        ("document", message.document),
        ("animation", message.animation),
        ("contact", message.contact),
        ("poll", message.poll),
        ("location", message.location),
        ("game", message.game),
        ("forward", message.forward_from),
        ("bots", from_user.is_bot),
        ("caption", message.caption),
        ("pin", message.pinned_message),
        ("inline", message.via_bot),
        ("previews", message.web_page),
        ("rtl", message.text and "\u202E" in message.text),
        ("media", any([message.photo, message.video, message.document, message.audio])),
        ("other", not any([
            message.text, message.photo, message.video, message.sticker, message.voice,
            message.document, message.audio, message.animation, message.contact,
            message.poll, message.location, message.game
        ]))
    ]

    # URL and mention checks
    if "url" in locks and message.entities:
        if any(e.type == "url" for e in message.entities):
            return await message.delete()
    if "mention" in locks and message.entities:
        if any(e.type == "mention" for e in message.entities):
            return await message.delete()

    # Loop through conditions and delete if locked
    for lock_type, condition in conditions:
        if lock_type in locks and condition:
            return await message.delete()