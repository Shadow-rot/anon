from pyrogram import Client, filters, enums
from pyrogram.types import ChatPrivileges, Message
from pyrogram.errors import ChatAdminRequired, RPCError
from functools import wraps
from AnonXMusic import app

BOT_OWNER_ID = 5147822244  # Replace with your actual user ID

def admin_required(*privileges):
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, message: Message):
            if not message.from_user:
                return await message.reply_text("You are anonymous. Please unhide your account to use this command.")
            try:
                member = await message.chat.get_member(message.from_user.id)
            except Exception as e:
                return await message.reply_text(f"Error: {e}")
            if member.status == enums.ChatMemberStatus.OWNER:
                return await func(client, message)
            elif member.status == enums.ChatMemberStatus.ADMINISTRATOR:
                if not member.privileges:
                    return await message.reply_text("Can't access your privileges.")
                missing = [p for p in privileges if not getattr(member.privileges, p, False)]
                if missing:
                    return await message.reply_text(f"You lack: {', '.join(missing)}")
                return await func(client, message)
            return await message.reply_text("You're not an admin.")
        return wrapper
    return decorator

async def extract_user_and_title(message: Message, client: Client):
    user = None
    title = None
    parts = message.text.split(maxsplit=2)[1:]

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        title = parts[0] if parts else None
    elif parts:
        try:
            user = await client.get_users(int(parts[0]) if parts[0].isdigit() else parts[0])
            title = parts[1] if len(parts) > 1 else None
        except Exception:
            await message.reply_text("I can't find that user.")
            return None, None

    if not user:
        await message.reply_text("Please reply to a user or provide a valid ID/username.")
        return None, None

    return user, title

def format_promotion_message(chat_name, user, admin, action, title=None):
    action_text = {
        "promote": "ᴩʀᴏᴍᴏᴛɪɴɢ",
        "fullpromote": "ғᴜʟʟ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "lowpromote": "ʟᴏᴡ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "demote": "ᴅᴇᴍᴏᴛɪɴɢ",
        "selfpromote": "sᴇʟғ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "selfdemote": "sᴇʟғ-ᴅᴇᴍᴏᴛɪɴɢ",
        "settitle": "ᴜᴘᴅᴀᴛɪɴɢ ᴀᴅᴍɪɴ ᴛɪᴛʟᴇ"
    }.get(action, "ᴜɴᴋɴᴏᴡɴ ᴀᴄᴛɪᴏɴ")

    text = f"» {action_text} ɪɴ {chat_name}\nᴜsᴇʀ : {user.mention}\nᴀᴅᴍɪɴ : {admin.mention if hasattr(admin, 'mention') else admin}"
    if title:
        text += f"\n**ɴᴇᴡ ᴛɪᴛʟᴇ:** `{title}`"
    return text

@app.on_message(filters.command("promote"))
@admin_required("can_promote_members")
async def promote_command_handler(client: Client, message: Message):
    user, _ = await extract_user_and_title(message, client)
    if not user:
        return
    try:
        await client.promote_chat_member(
            message.chat.id, user.id,
            ChatPrivileges(
                can_delete_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_chat=True,
                can_manage_video_chats=True,
                is_anonymous=False,
            )
        )
        await message.reply_text(format_promotion_message(
            message.chat.title, user, message.from_user, "promote"
        ))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("title"))
@admin_required("can_promote_members")
async def set_title_handler(client: Client, message: Message):
    user, title = await extract_user_and_title(message, client)
    if not user or not title:
        return await message.reply_text("Usage: `/title @username NewTitle`")

    try:
        await client.set_administrator_title(message.chat.id, user.id, title)
        await message.reply_text(format_promotion_message(
            message.chat.title, user, message.from_user, "settitle", title
        ))
    except ChatAdminRequired:
        await message.reply_text("I need admin rights to change the title.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("demote"))
@admin_required("can_promote_members")
async def demote_command_handler(client: Client, message: Message):
    user, _ = await extract_user_and_title(message, client)
    if not user:
        return
    try:
        await client.promote_chat_member(message.chat.id, user.id, ChatPrivileges())
        await message.reply_text(format_promotion_message(
            message.chat.title, user, message.from_user, "demote"
        ))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("selfpromote"))
async def selfpromote_command_handler(client: Client, message: Message):
    if message.from_user.id != BOT_OWNER_ID:
        return await message.reply_text("Only the bot owner can use this command.")

    try:
        await client.promote_chat_member(
            message.chat.id, message.from_user.id,
            ChatPrivileges(
                can_manage_chat=True,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                is_anonymous=False,
                can_manage_video_chats=True,
            )
        )
        await message.reply_text(format_promotion_message(
            message.chat.title, message.from_user, "Bot Owner", "selfpromote"
        ))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("selfdemote"))
async def selfdemote_command_handler(client: Client, message: Message):
    if message.from_user.id != BOT_OWNER_ID:
        return await message.reply_text("Only the bot owner can use this command.")

    try:
        await client.promote_chat_member(message.chat.id, message.from_user.id, ChatPrivileges())
        await message.reply_text(format_promotion_message(
            message.chat.title, message.from_user, "Bot Owner", "selfdemote"
        ))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")