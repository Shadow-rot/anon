from pyrogram import Client, filters, enums
from pyrogram.types import ChatPrivileges
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from functools import wraps
from AnonXMusic import app

BOT_OWNER_ID = 5147822244  # Replace with your actual Telegram user ID

def mention(user):
    return user.mention if user else "Unknown User"

def admin_required(*privileges):
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
    user = None
    title = None
    cmd = message.text.strip().split()[0]
    text = message.text[len(cmd):].strip()

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if not user:
            await message.reply_text("I can't find the user in the replied message.")
            return None, None
        title = text if text else None
    else:
        args = text.split(maxsplit=1)
        if not args:
            await message.reply_text("Please specify a user or reply to a user's message.")
            return None, None

        user_arg = args[0]

        try:
            if user_arg.isdigit():
                user = await client.get_users(int(user_arg))  # User ID
            else:
                user = await client.get_users(user_arg)  # Username or Mention
        except UserNotParticipant:
            await message.reply_text("The user is not in this chat.")
            return None, None
        except Exception:
            await message.reply_text("I can't find that user.")
            return None, None

        title = args[1] if len(args) > 1 else None

    return user, title

def format_promotion_message(chat_name, user_mention, admin_mention, action):
    action_text = {
        "promote": "ᴩʀᴏᴍᴏᴛɪɴɢ",
        "fullpromote": "ғᴜʟʟ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "lowpromote": "ʟᴏᴡ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "demote": "ᴅᴇᴍᴏᴛɪɴɢ"
    }.get(action, "ᴜɴᴋɴᴏᴡɴ ᴀᴄᴛɪᴏɴ")

    return (
        f"» {action_text} ᴀ ᴜsᴇʀ ɪɴ {chat_name}\n"
        f"ᴜsᴇʀ : {user_mention}\n"
        f"ᴀᴅᴍɪɴ : {admin_mention}"
    )

@app.on_message(filters.command("promote"))
@admin_required("can_promote_members")
async def promote_command_handler(client, message):
    user, title = await extract_user_and_title(message, client)
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

        if title:
            await client.set_administrator_title(message.chat.id, user.id, title)

        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "promote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("fullpromote"))
@admin_required("can_promote_members")
async def fullpromote_command_handler(client, message):
    user, _ = await extract_user_and_title(message, client)
    if not user:
        return
    try:
        await client.promote_chat_member(
            message.chat.id, user.id,
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

        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "fullpromote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("lowpromote"))
@admin_required("can_promote_members")
async def lowpromote_command_handler(client, message):
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
                is_anonymous=False,
            )
        )

        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "lowpromote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("demote"))
@admin_required("can_promote_members")
async def demote_command_handler(client, message):
    user, _ = await extract_user_and_title(message, client)
    if not user:
        return
    try:
        await client.promote_chat_member(message.chat.id, user.id, ChatPrivileges(
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
            is_anonymous=False,
        ))

        await message.reply_text(format_promotion_message(message.chat.title, mention(user), mention(message.from_user), "demote"))
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("selfdemote"))
async def selfdemote_command_handler(client, message):
    if message.from_user.id != BOT_OWNER_ID:
        await message.reply_text("Only the bot owner can use this command.")
        return

    try:
        await client.promote_chat_member(
            message.chat.id, message.from_user.id, 
            ChatPrivileges(
                can_change_info=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_chat=False,
                can_manage_video_chats=False,
                is_anonymous=False,
            )
        )

        user_mention = mention(message.from_user)
        chat_name = message.chat.title
        msg = f"» sᴇʟғ-ᴅᴇᴍᴏᴛᴇ ɪɴ {chat_name}\nᴜsᴇʀ : {user_mention}\nᴘᴏᴡᴇʀ ʀᴇᴠᴏᴋᴇᴅ ✅"
        await message.reply_text(msg)
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")