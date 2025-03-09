from pyrogram import Client, filters, enums
from pyrogram.types import ChatPrivileges
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, RPCError
from functools import wraps
from AnonXMusic import app

BOT_OWNER_ID = 5147822244  # Replace with your actual Telegram user ID

def mention(user):
    """Generate a mention without exposing user ID."""
    return f"[{user.first_name}](tg://user?id={user.id})" if user else "Unknown User"

def admin_required(*privileges):
    """Check if the user has the required admin privileges."""
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            if not message.from_user:
                await message.reply_text("You are an anonymous admin. Please unhide your account to use this command.")
                return

            member = await message.chat.get_member(message.from_user.id)
            if member.status == enums.ChatMemberStatus.OWNER:
                return await func(client, message)
            elif member.status == enums.ChatMemberStatus.ADMINISTRATOR:
                if not member.privileges:
                    await message.reply_text("Cannot retrieve your admin privileges.")
                    return
                missing_privileges = [priv for priv in privileges if not getattr(member.privileges, priv, False)]
                if missing_privileges:
                    await message.reply_text(f"You don't have the required permissions: {', '.join(missing_privileges)}")
                    return
                return await func(client, message)
            else:
                await message.reply_text("You are not an admin.")
                return
        return wrapper
    return decorator

async def extract_user_and_title(message, client):
    """Extracts a user and title from a message (by ID, username, or reply)."""
    user = None
    title = None
    text = message.text.strip().split(maxsplit=1)[1:] if len(message.text.split()) > 1 else []

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        title = text[0] if text else None
    elif text:
        user_arg = text[0].strip()
        title = text[1] if len(text) > 1 else None
        try:
            user = await client.get_users(int(user_arg) if user_arg.isdigit() else user_arg)
        except Exception:
            await message.reply_text("I can't find that user.")
            return None, None

    if not user:
        await message.reply_text("Please provide a valid user (ID, username, or reply).")
    
    return user, title

def format_promotion_message(chat_name, user_mention, admin_mention, action, title=None):
    """Formats the message for admin actions."""
    action_text = {
        "promote": "ᴩʀᴏᴍᴏᴛɪɴɢ",
        "fullpromote": "ғᴜʟʟ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "lowpromote": "ʟᴏᴡ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "demote": "ᴅᴇᴍᴏᴛɪɴɢ",
        "selfpromote": "sᴇʟғ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "selfdemote": "sᴇʟғ-ᴅᴇᴍᴏᴛɪɴɢ",
        "settitle": "ᴜᴘᴅᴀᴛɪɴɢ ᴀᴅᴍɪɴ ᴛɪᴛʟᴇ"
    }.get(action, "ᴜɴᴋɴᴏᴡɴ ᴀᴄᴛɪᴏɴ")

    text = f"» {action_text} ɪɴ {chat_name}\nᴜsᴇʀ : {user_mention}\nᴀᴅᴍɪɴ : {admin_mention}"
    if title:
        text += f"\n**ɴᴇᴡ ᴛɪᴛʟᴇ:** `{title}`"
    return text

@app.on_message(filters.command("promote"))
@admin_required("can_promote_members")
async def promote_command_handler(client, message):
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

        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "promote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("title"))
@admin_required("can_promote_members")
async def set_title_handler(client, message):
    user, title = await extract_user_and_title(message, client)
    if not user or not title:
        return await message.reply_text("Usage: `/title @username NewTitle`")

    try:
        await client.set_administrator_title(message.chat.id, user.id, title)
        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "settitle", title))
    except ChatAdminRequired:
        await message.reply_text("I need admin rights to change the title.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("demote"))
@admin_required("can_promote_members")
async def demote_command_handler(client, message):
    user, _ = await extract_user_and_title(message, client)
    if not user:
        return
    try:
        await client.promote_chat_member(message.chat.id, user.id, ChatPrivileges())
        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "demote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("selfpromote"))
async def selfpromote_command_handler(client, message):
    if message.from_user.id != BOT_OWNER_ID:
        await message.reply_text("Only the bot owner can use this command.")
        return

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

        await message.reply_text(format_promotion_message(message.chat.title, mention(message.from_user), "Bot Owner", "selfpromote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("selfdemote"))
async def selfdemote_command_handler(client, message):
    if message.from_user.id != BOT_OWNER_ID:
        await message.reply_text("Only the bot owner can use this command.")
        return

    try:
        await client.promote_chat_member(message.chat.id, message.from_user.id, ChatPrivileges())
        await message.reply_text(format_promotion_message(message.chat.title, mention(message.from_user), "Bot Owner", "selfdemote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")