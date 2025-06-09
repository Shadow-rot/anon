from pyrogram import filters, enums
from pyrogram.types import ChatPermissions
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, RPCError
import asyncio

from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check
from AnonXMusic.utils.autofix import auto_fix_handler  # <-- add this line
from config import OWNER_ID


# Helper: Extract user and optional reason from message
async def extract_user_and_reason(message: Message, client):
    args = message.text.split()
    reason = None
    user = None

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if len(args) > 1:
            reason = message.text.partition(args[1])[2].strip() or None
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


# BUTTONS FOR HELP MENU

MODERATION_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("ban", callback_data="mod_ban"),
            InlineKeyboardButton("unban", callback_data="mod_unban"),
        ],
        [
            InlineKeyboardButton("mute", callback_data="mod_mute"),
            InlineKeyboardButton("unmute", callback_data="mod_unmute"),
        ],
        [
            InlineKeyboardButton("kick", callback_data="mod_kick"),
        ],
        [InlineKeyboardButton("close", callback_data="mod_close")],
    ]
)


# --- Commands ---


@app.on_message(filters.command("ban") & filters.group)
@auto_fix_handler
async def ban_command(client, message: Message):
    if not await admin_check(message) and message.from_user.id != OWNER_ID:
        return await message.reply_text("You are not allowed to use this command.")
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        text = f"Banned ╰┈➤ {user.mention}\nBanned by ╰┈➤ {message.from_user.mention}"
        if reason:
            text += f"\nReason: {reason}"

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unban",
                        callback_data=f"unban:{message.chat.id}:{user.id}"
                    )
                ]
            ]
        )
        await message.reply_text(text, reply_markup=buttons)
    except ChatAdminRequired:
        await message.reply_text("I need admin rights with ban permissions to perform this action.")
    except UserAdminInvalid:
        await message.reply_text("Cannot ban an admin or the group owner.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")


@app.on_callback_query(filters.regex(r"^unban:(-?\d+):(\d+)$"))
@auto_fix_handler
async def unban_callback(client, callback_query: CallbackQuery):
    chat_id = int(callback_query.matches[0].group(1))
    user_id = int(callback_query.matches[0].group(2))
    from_user = callback_query.from_user

    # Check if user is admin or OWNER
    try:
        member = await client.get_chat_member(chat_id, from_user.id)
        if not (
            (member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER])
            and member.privileges.can_restrict_members
            or from_user.id == OWNER_ID
        ):
            return await callback_query.answer("You are not allowed to unban users.", show_alert=True)

        await client.unban_chat_member(chat_id, user_id)
        await callback_query.message.edit_text(
            f"User [ID: {user_id}] has been unbanned by {from_user.mention}."
        )
    except ChatAdminRequired:
        await callback_query.answer("I need admin rights with unban permissions.", show_alert=True)
    except RPCError as e:
        await callback_query.answer(f"Error: {e}", show_alert=True)


@app.on_message(filters.command("unban") & filters.group)
@auto_fix_handler
async def unban_command(client, message: Message):
    if not await admin_check(message) and message.from_user.id != OWNER_ID:
        return await message.reply_text("You are not allowed to use this command.")
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.unban_chat_member(message.chat.id, user.id)
        text = f"{user.mention} was unbanned by {message.from_user.mention}"
        if reason:
            text += f"\nReason: {reason}"
        await message.reply_text(text)
    except ChatAdminRequired:
        await message.reply_text("I need admin rights with unban permissions to perform this action.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("mute") & filters.group)
@auto_fix_handler
async def mute_command(client, message: Message):
    if not await admin_check(message) and message.from_user.id != OWNER_ID:
        return await message.reply_text("You are not allowed to use this command.")
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        text = f"{user.mention} was muted by {message.from_user.mention}"
        if reason:
            text += f"\nReason: {reason}"
        await message.reply_text(text)
    except ChatAdminRequired:
        await message.reply_text("I need admin rights with mute permissions to perform this action.")
    except UserAdminInvalid:
        await message.reply_text("Cannot mute an admin or the group owner.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("unmute") & filters.group)
@auto_fix_handler
async def unmute_command(client, message: Message):
    if not await admin_check(message) and message.from_user.id != OWNER_ID:
        return await message.reply_text("You are not allowed to use this command.")
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        text = f"{user.mention} was unmuted by {message.from_user.mention}"
        if reason:
            text += f"\nReason: {reason}"
        await message.reply_text(text)
    except ChatAdminRequired:
        await message.reply_text("I need admin rights with unmute permissions to perform this action.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("kick") & filters.group)
@auto_fix_handler
async def kick_command(client, message: Message):
    if not await admin_check(message) and message.from_user.id != OWNER_ID:
        return await message.reply_text("You are not allowed to use this command.")
    user, reason = await extract_user_and_reason(message, client)
    if not user:
        return
    try:
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply_text("Cannot kick an admin or the group owner.")

        await client.ban_chat_member(message.chat.id, user.id)
        await asyncio.sleep(0.1)  # short delay to allow ban to register
        await client.unban_chat_member(message.chat.id, user.id)
        text = f"{user.mention} was kicked by {message.from_user.mention}"
        if reason:
            text += f"\nReason: {reason}"
        await message.reply_text(text)
    except ChatAdminRequired:
        await message.reply_text("I need admin rights with ban permissions to perform this action.")
    except UserAdminInvalid:
        await message.reply_text("Cannot kick an admin or the group owner.")
    except RPCError as e:
        await message.reply_text(f"Error: {e}")


# --- Help Menu ---


HELP_TEXT = (
    "<b>moderation commands help menu</b>\n\n"
    "ban - ban a user\n"
    "unban - unban a user\n"
    "mute - mute a user\n"
    "unmute - unmute a user\n"
    "kick - kick a user\n\n"
    "<b>usage:</b>\n"
    "• reply to a user or specify by username/userid\n"
    "• optionally add reason after command\n"
    "example: /ban spamming\n\n"
    "<b>note:</b> You must be admin or bot owner to use these commands."
)


@app.on_message(filters.command("modhelp") & filters.group)
@auto_fix_handler
async def mod_help_command(client, message: Message):
    await message.reply_text(
        "<b>choose a command to view help:</b>",
        reply_markup=MODERATION_BUTTONS
    )


@app.on_callback_query(filters.regex(r"^mod_(ban|unban|mute|unmute|kick|close)$"))
@auto_fix_handler
async def mod_help_buttons(client, callback_query: CallbackQuery):
    cmd = callback_query.data.split("_")[1]

    if cmd == "close":
        return await callback_query.message.delete()

    help_texts = {
        "ban": (
            "<b>ban command help</b>\n\n"
            "• Ban a user by replying or mentioning.\n"
            "• Usage: /ban [reason]\n"
            "• You must have ban rights."
        ),
        "unban": (
            "<b>unban command help</b>\n\n"
            "• Unban a user by replying or mentioning.\n"
            "• Usage: /unban [reason]\n"
            "• You must have unban rights."
        ),
        "mute": (
            "<b>mute command help</b>\n\n"
            "• Mute a user by replying or mentioning.\n"
            "• Usage: /mute [reason]\n"
            "• You must have mute rights."
        ),
        "unmute": (
            "<b>unmute command help</b>\n\n"
            "• Unmute a user by replying or mentioning.\n"
            "• Usage: /unmute [reason]\n"
            "• You must have unmute rights."
        ),
        "kick": (
            "<b>kick command help</b>\n\n"
            "• Kick a user by replying or mentioning.\n"
            "• Usage: /kick [reason]\n"
            "• You must have ban rights."
        ),
    }

    text = help_texts.get(cmd, HELP_TEXT)
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back", callback_data="mod_help")],
                [InlineKeyboardButton("Close", callback_data="mod_close")],
            ]
        )
    )


@app.on_callback_query(filters.regex("mod_help"))
@auto_fix_handler
async def mod_help_back(client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "<b>choose a command to view help:</b>",
        reply_markup=MODERATION_BUTTONS
    )