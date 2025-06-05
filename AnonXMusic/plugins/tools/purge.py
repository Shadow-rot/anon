from asyncio import sleep
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check
from config import OWNER_ID
from collections.abc import Iterable


# Helper: Check if user is owner (int or list)
def is_owner(user_id: int) -> bool:
    owners = OWNER_ID if isinstance(OWNER_ID, Iterable) and not isinstance(OWNER_ID, (str, bytes)) else [OWNER_ID]
    return user_id in owners


# Chunking for bulk delete
def divide_chunks(lst, n=100):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# Confirm Inline Markup
def confirm_markup(cmd: str, from_id: int, user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirmpurge|{cmd}|{from_id}|{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancelpurge")
        ]
    ])


# ────────────────────────────── /purge ────────────────────────────── #
@app.on_message(filters.command("purge") & filters.group)
async def purge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("🚫 This command works only in supergroups.")

    if not message.reply_to_message:
        return await message.reply("ℹ️ Reply to a message to start purging from that message to this one.")

    is_admin = await admin_check(message)
    if not is_owner(message.from_user.id) and not is_admin:
        return await message.reply("❗ You must be an admin or owner to use this command.")

    await message.reply(
        f"🧹 Do you want to delete messages from ID <code>{message.reply_to_message.id}</code> to <code>{message.id}</code>?\n\n"
        "⚠️ Messages older than <b>2 days</b> can't be deleted due to Telegram limits.",
        reply_markup=confirm_markup("purge", message.reply_to_message.id, message.from_user.id)
    )


# ────────────────────────────── /spurge ────────────────────────────── #
@app.on_message(filters.command("spurge") & filters.group)
async def spurge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("🚫 This command works only in supergroups.")

    if not message.reply_to_message:
        return await message.reply("ℹ️ Reply to a message to silently purge from that message to this one.")

    is_admin = await admin_check(message)
    if not is_owner(message.from_user.id) and not is_admin:
        return await message.reply("❗ You must be an admin or owner to use this command.")

    await message.reply(
        f"🤫 Silent purge from message ID <code>{message.reply_to_message.id}</code> to <code>{message.id}</code>?\n\n"
        "⚠️ Older messages (48h+) may not be deletable due to Telegram restrictions.",
        reply_markup=confirm_markup("spurge", message.reply_to_message.id, message.from_user.id)
    )


# ────────────────────────────── /del ────────────────────────────── #
@app.on_message(filters.command("del") & filters.group)
async def del_message(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("🚫 This command works only in supergroups.")

    if not message.reply_to_message:
        return await message.reply("ℹ️ Reply to the message you want to delete.")

    is_admin = await admin_check(message)
    if not is_owner(message.from_user.id) and not is_admin:
        return await message.reply("❗ Only admins or owners can use this command.")

    try:
        await client.delete_messages(message.chat.id, [message.reply_to_message.id, message.id])
    except MessageDeleteForbidden:
        await message.reply("🚫 I don't have permission to delete messages.")
    except RPCError as e:
        await message.reply(f"⚠️ Telegram error: {e}")


# ─────────────────────── Confirmation Callback ─────────────────────── #
@app.on_callback_query(filters.regex(r"^confirmpurge\|"))
async def confirm_purge(client, query: CallbackQuery):
    try:
        _, cmd, start_id, expected_uid = query.data.split("|")
        start_id, expected_uid = int(start_id), int(expected_uid)
        user_id = query.from_user.id

        if user_id != expected_uid:
            return await query.answer("❌ This isn't your purge request!", show_alert=True)

        message = query.message
        end_id = message.reply_to_message.id if message.reply_to_message else message.id
        ids = list(range(start_id, end_id))

        # Telegram doesn’t allow deleting >100 or old messages
        for chunk in divide_chunks(ids):
            await client.delete_messages(chat_id=message.chat.id, message_ids=chunk, revoke=True)

        await message.edit_text(f"✅ Successfully purged <b>{len(ids)}</b> messages.")
        await sleep(3)
        await message.delete()

    except MessageDeleteForbidden:
        await query.message.edit_text("🚫 I lack permission to delete some messages.")
    except RPCError as e:
        await query.message.edit_text(f"⚠️ Telegram error: {e}")


# ─────────────────────── Cancel Callback ─────────────────────── #
@app.on_callback_query(filters.regex(r"^cancelpurge$"))
async def cancel_purge(client, query: CallbackQuery):
    await query.message.edit_text("❎ Purge cancelled.")