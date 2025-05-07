from pyrogram import Client, filters, enums
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
import asyncio
from functools import wraps
from AnonXMusic import app

BOT_OWNER_ID = 5147822244  # Replace with your actual bot owner ID

def admin_required(func):
    @wraps(func)
    async def wrapper(client, message):
        if message.from_user.id == BOT_OWNER_ID:
            return await func(client, message)
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
            if user_arg.isdigit():
                user = await client.get_users(int(user_arg))
            else:
                user = await client.get_users(user_arg)
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
        msg = f"Banned ╰┈➤ {user.mention}\nbanned by ╰┈➤ {message.from_user.mention}"
        if reason:
            msg += f"\nReason: {reason}"

        keyboard = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "Unban",
                    callback_data=f"unban:{message.chat.id}:{user.id}"
                )
            ]]
        )

        await message.reply_text(msg, reply_markup=keyboard)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot ban an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

@app.on_callback_query(filters.regex(r"^unban:(-?\d+):(\d+)$"))
async def unban_callback_handler(client, callback_query: CallbackQuery):
    chat_id = int(callback_query.matches[0].group(1))
    user_id = int(callback_query.matches[0].group(2))
    from_user = callback_query.from_user

    try:
        member = await client.get_chat_member(chat_id, from_user.id)
        if not (
            member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            and member.privileges.can_restrict_members
        ):
            return await callback_query.answer("You're not allowed to unban.", show_alert=True)

        await client.unban_chat_member(chat_id, user_id)
        await callback_query.message.edit_text(f"User [ID: {user_id}] has been unbanned by {from_user.mention}.")
    except ChatAdminRequired:
        await callback_query.answer("I need unban permissions.", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"Error: {e}", show_alert=True)

@app.on_message(filters.command("unban"))
@admin_required
async def unban_command_handler(client, message):
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.unban_chat_member(message.chat.id, user.id)
        msg = f"{user.mention} was unbanned by {message.from_user.mention}"
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
        msg = f"{user.mention} was muted by {message.from_user.mention}"
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
        msg = f"{user.mention} was unmuted by {message.from_user.mention}"
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
        msg = f"{user.mention} was kicked by {message.from_user.mention}"
        if reason:
            msg += f"\nReason: {reason}"
        await message.reply_text(msg)
    except ChatAdminRequired:
        await message.reply_text("I need to be an admin with ban permissions.")
    except UserAdminInvalid:
        await message.reply_text("I cannot kick an admin.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")