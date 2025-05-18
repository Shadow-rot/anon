from pyrogram import Client, filters, enums
from pyrogram.types import ChatPrivileges, Message
from pyrogram.errors import ChatAdminRequired, RPCError
from functools import wraps
from AnonXMusic import app  # Replace with your bot instance

BOT_OWNER_ID = 5147822244  # Replace with your Telegram user ID


def admin_required(*privileges):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message: Message):
            if not message.from_user:
                return await message.reply_text(
                    "Anonymous admins can't use this command. Please unhide your account."
                )

            member = await message.chat.get_member(message.from_user.id)
            if member.status == enums.ChatMemberStatus.OWNER:
                return await func(client, message)
            elif member.status == enums.ChatMemberStatus.ADMINISTRATOR:
                if not member.privileges:
                    return await message.reply_text("Cannot retrieve your admin privileges.")
                missing = [p for p in privileges if not getattr(member.privileges, p, False)]
                if missing:
                    return await message.reply_text(f"You lack permissions: {', '.join(missing)}")
                return await func(client, message)
            else:
                return await message.reply_text("You're not an admin.")
        return wrapper
    return decorator


async def extract_user_and_title(message: Message, client: Client):
    user = None
    title = None
    args = message.text.strip().split(maxsplit=1)[1:] if len(message.text.split()) > 1 else []

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        title = args[0] if args else None
    elif args:
        user_arg = args[0].strip()
        title = args[1] if len(args) > 1 else None
        try:
            user = await client.get_users(int(user_arg) if user_arg.isdigit() else user_arg)
        except Exception:
            await message.reply_text("I couldn't find that user.")
            return None, None

    if not user:
        await message.reply_text("Reply to a user or provide a username/ID.")
    return user, title


def format_promotion_message(chat_name, user, admin, action, title=None):
    actions = {
        "promote": "ᴩʀᴏᴍᴏᴛɪɴɢ",
        "fullpromote": "ғᴜʟʟ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "lowpromote": "ʟᴏᴡ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "demote": "ᴅᴇᴍᴏᴛɪɴɢ",
        "selfpromote": "sᴇʟғ-ᴘʀᴏᴍᴏᴛɪᴏɴ",
        "selfdemote": "sᴇʟғ-ᴅᴇᴍᴏᴛɪɴɢ",
        "settitle": "ᴜᴘᴅᴀᴛɪɴɢ ᴀᴅᴍɪɴ ᴛɪᴛʟᴇ"
    }.get(action, "ᴀᴅᴍɪɴ ᴀᴄᴛɪᴏɴ")

    text = f"» {actions} ɪɴ {chat_name}\nᴜsᴇʀ : {user.mention}\nᴀᴅᴍɪɴ : {admin.mention}"
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
            message.chat.id,
            user.id,
            ChatPrivileges(
                can_delete_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_chat=True,
                can_manage_video_chats=True,
                is_anonymous=False,
            ),
        )
        await message.reply_text(
            format_promotion_message(message.chat.title, user, message.from_user, "promote")
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


@app.on_message(filters.command("demote"))
@admin_required("can_promote_members")
async def demote_command_handler(client: Client, message: Message):
    user, _ = await extract_user_and_title(message, client)
    if not user:
        return

    try:
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status != enums.ChatMemberStatus.ADMINISTRATOR:
            return await message.reply_text(f"{user.mention} is already a normal member.")

        # This fully removes admin status (not just clears powers)
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            privileges=None  # Fully demote from admin
        )

        await message.reply_text(f"{user.mention} has been completely demoted from admin.")
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
        await message.reply_text(
            format_promotion_message(message.chat.title, user, message.from_user, "settitle", title)
        )
    except ChatAdminRequired:
        await message.reply_text("I need admin rights to change the title.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("selfpromote"))
async def selfpromote_command_handler(client: Client, message: Message):
    if message.from_user.id != BOT_OWNER_ID:
        return await message.reply_text("Only the bot owner can use this command.")
    try:
        await client.promote_chat_member(
            message.chat.id,
            message.from_user.id,
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
            ),
        )
        await message.reply_text(
            format_promotion_message(message.chat.title, message.from_user, message.from_user, "selfpromote")
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


@app.on_message(filters.command("selfdemote"))
async def selfdemote_command_handler(client: Client, message: Message):
    if message.from_user.id != BOT_OWNER_ID:
        return await message.reply_text("Only the bot owner can use this command.")
    try:
        await client.promote_chat_member(message.chat.id, message.from_user.id, ChatPrivileges())
        await message.reply_text(
            format_promotion_message(message.chat.title, message.from_user, message.from_user, "selfdemote")
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")