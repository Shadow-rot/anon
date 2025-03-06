from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
import asyncio
import datetime
from functools import wraps
from AnonXMusic import app


# Mention Function (Uses Only First Name)
def mention(name):
    return name


# Admin Check Decorator (Owners Can Always Execute Commands)
def admin_required(func):
    @wraps(func)
    async def wrapper(client, message):
        if not message.from_user:
            return await message.reply_text("I can't verify your permissions.")
        
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        
        # If user is OWNER, bypass admin checks
        if chat_member.status == enums.ChatMemberStatus.OWNER:
            return await func(client, message)

        # Check if user is an ADMIN with required privileges
        if chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR and chat_member.privileges.can_restrict_members:
            return await func(client, message)

        # If not an admin, deny command
        await message.reply_text("You don't have permission to perform this action.")
    return wrapper


# Extract User and Reason from Command
async def extract_user_and_reason(message, client):
    args = message.text.split()
    reason = None
    user = None

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if len(args) > 1:
            reason = message.text.split(None, 1)[1]
    elif len(args) > 1:
        user_arg = args[1]
        reason = message.text.partition(args[1])[2].strip() or None
        try:
            user = await client.get_users(user_arg)
        except Exception:
            return await message.reply_text("I can't find that user.")
    else:
        return await message.reply_text("Please specify a user or reply to a user's message.")

    return user.id, user.first_name, reason


# Ban Command (Owners Can Ban Anyone)
@app.on_message(filters.command("ban"))
@admin_required
async def ban_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return

    try:
        chat_member = await client.get_chat_member(message.chat.id, user_id)

        # Prevent bot from banning itself
        if user_id == client.me.id:
            return await message.reply_text("I can't ban myself.")

        # Owners can ban anyone, admins can't ban other admins
        if chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            issuer = await client.get_chat_member(message.chat.id, message.from_user.id)
            if issuer.status != enums.ChatMemberStatus.OWNER:
                return await message.reply_text("I can't ban another admin. Only owners can do that.")

        await client.ban_chat_member(message.chat.id, user_id)

        user_mention = mention(first_name)
        admin_mention = mention(message.from_user.first_name)

        msg = f"{user_mention} was banned by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        
        await message.reply_text(msg)

    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


# Unban Command
@app.on_message(filters.command("unban"))
@admin_required
async def unban_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return

    try:
        await client.unban_chat_member(message.chat.id, user_id)

        user_mention = mention(first_name)
        admin_mention = mention(message.from_user.first_name)

        msg = f"{user_mention} was unbanned by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        
        await message.reply_text(msg)

    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with unban permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


# Kick Command
@app.on_message(filters.command("kick"))
@admin_required
async def kick_command_handler(client, message):
    user_id, first_name, reason = await extract_user_and_reason(message, client)
    if not user_id:
        return

    try:
        chat_member = await client.get_chat_member(message.chat.id, user_id)

        # Owners can kick anyone, admins can't kick other admins
        if chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            issuer = await client.get_chat_member(message.chat.id, message.from_user.id)
            if issuer.status != enums.ChatMemberStatus.OWNER:
                return await message.reply_text("I can't kick another admin. Only owners can do that.")

        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(0.1)
        await client.unban_chat_member(message.chat.id, user_id)

        user_mention = mention(first_name)
        admin_mention = mention(message.from_user.first_name)

        msg = f"{user_mention} was kicked by {admin_mention}"
        if reason:
            msg += f"\nReason: {reason}"
        
        await message.reply_text(msg)

    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")