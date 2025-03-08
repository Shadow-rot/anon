from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
import asyncio
from functools import wraps
from AnonXMusic import app

BOT_OWNER_ID = 5147822244  # Replace with your actual bot owner ID

def mention(user):
    return user.mention if user else "Unknown User"

def admin_required(func):
    @wraps(func)
    async def wrapper(client, message):
        if message.from_user.id == BOT_OWNER_ID:
            return await func(client, message)  # Allow bot owner to use commands
        member = await message.chat.get_member(message.from_user.id)
        if (
            member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            and member.privileges.can_restrict_members
        ):
            return await func(client, message)
        await message.reply_text("You don't have permission to perform this action.")
    return wrapper

async def extract_user_and_reason(message, client):
    args = message.text.split()
    reason = None
    user = None
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if len(args) > 1:
            reason = message.text.partition(args[1])[2].strip()
    elif len(args) > 1:
        user_arg = args[1]
        reason = message.text.partition(args[1])[2].strip() or None
        try:
            user = await client.get_users(int(user_arg) if user_arg.isdigit() else user_arg)
        except Exception:
            await message.reply_text("I can't find that user.")
            return None, None
    else:
        await message.reply_text("Please specify a user or reply to a user's message.")
        return None, None
    return user, reason

@app.on_message(filters.command("ban"))
@admin_required
async def ban_command_handler(client, message):
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        msg = f"{mention(user)} was banned by {mention(message.from_user)}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("unban"))
@admin_required
async def unban_command_handler(client, message):
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.unban_chat_member(message.chat.id, user.id)
        msg = f"{mention(user)} was unbanned by {mention(message.from_user)}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("mute"))
@admin_required
async def mute_command_handler(client, message):
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        msg = f"{mention(user)} was muted by {mention(message.from_user)}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with mute permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot mute an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("unmute"))
@admin_required
async def unmute_command_handler(client, message):
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        msg = f"{mention(user)} was unmuted by {mention(message.from_user)}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with unmute permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_message(filters.command("kick"))
@admin_required
async def kick_command_handler(client, message):
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("I cannot kick an admin.")
            return
        await client.ban_chat_member(message.chat.id, user.id)
        await asyncio.sleep(0.1)
        await client.unban_chat_member(message.chat.id, user.id)
        msg = f"{mention(user)} was kicked by {mention(message.from_user)}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot kick an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")