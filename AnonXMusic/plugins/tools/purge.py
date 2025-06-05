from asyncio import sleep
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check
from config import OWNER_ID


# Ensure OWNER_ID is a list
OWNER_ID = [OWNER_ID] if isinstance(OWNER_ID, int) else OWNER_ID


# ─────────── Helper Functions ───────────

def divide_chunks(lst, n=100):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def confirm_markup(cmd: str, start_id: int, user_id: int, reason: str = ""):
    data = f"{cmd}|{start_id}|{user_id}|{reason}" if reason else f"{cmd}|{start_id}|{user_id}"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("purge", callback_data=f"confirmpurge|{data}"),
            InlineKeyboardButton("cancel", callback_data="cancelpurge")
        ]
    ])


# ─────────── Commands ───────────

@app.on_message(filters.command("purge") & filters.group)
async def purge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("reply to a message to start purge.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("you're not an admin.")

    reason = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    await message.reply(
        f"delete messages from {message.reply_to_message.id} to {message.id}?",
        reply_markup=confirm_markup("purge", message.reply_to_message.id, message.from_user.id, reason)
    )


@app.on_message(filters.command("spurge") & filters.group)
async def spurge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("reply to a message to start spurge.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("you're not an admin.")

    try:
        start = message.reply_to_message.id
        end = message.id
        ids = list(range(start, end))

        for chunk in divide_chunks(ids):
            await client.delete_messages(chat_id=message.chat.id, message_ids=chunk, revoke=True)

    except MessageDeleteForbidden:
        await message.reply("can't delete message. missing permissions.")
    except RPCError as e:
        await message.reply(f"error: {e}")


@app.on_message(filters.command("del") & filters.group)
async def del_message(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("reply to a message to delete it.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("you're not an admin.")

    try:
        await client.delete_messages(message.chat.id, [message.reply_to_message.id, message.id])
    except MessageDeleteForbidden:
        await message.reply("can't delete message. missing permissions.")
    except RPCError as e:
        await message.reply(f"error: {e}")


# ─────────── Confirm Purge Logic ───────────

@app.on_callback_query(filters.regex(r"^confirmpurge\|"))
async def confirm_purge(client, query: CallbackQuery):
    data = query.data.split("|")
    if len(data) < 4:
        return await query.message.edit_text("invalid purge request.")

    cmd = data[1]
    start_id = int(data[2])
    expected_uid = int(data[3])
    reason = data[4] if len(data) > 4 else ""
    user_id = query.from_user.id

    if user_id != expected_uid:
        return await query.answer("not your purge request.", show_alert=True)

    try:
        message = query.message
        end_id = message.reply_to_message.id if message.reply_to_message else message.id
        ids = list(range(start_id, end_id))

        for chunk in divide_chunks(ids):
            await client.delete_messages(chat_id=message.chat.id, message_ids=chunk, revoke=True)

        reply_text = f"deleted {len(ids)} messages."
        if reason:
            reply_text += f"\nreason: <i>{reason}</i>"

        await message.edit_text(reply_text)
        await sleep(3)
        await message.delete()

    except MessageDeleteForbidden:
        await query.message.edit_text("can't delete messages. missing permissions.")
    except RPCError as e:
        await query.message.edit_text(f"error: {e}")


@app.on_callback_query(filters.regex(r"^cancelpurge$"))
async def cancel_purge(client, query: CallbackQuery):
    await query.message.edit_text("purge cancelled.")


# ─────────── Help Menu ───────────

PURGE_HELP = (
    "<b><u>purge command help</u></b>\n\n"
    "• deletes messages from the replied message up to your command message.\n"
    "• works with or without a reason. example:\n"
    "<code>/purge spam</code>\n\n"
    "<b>how to use:</b>\n"
    "→ reply to a message\n"
    "→ send /purge or /purge [reason]\n\n"
    "<b>limits:</b>\n"
    "• cannot delete messages older than ~48 hours.\n"
    "• you must be an admin or sudo user."
)

SPURGE_HELP = (
    "<b><u>spurge command help</u></b>\n\n"
    "• silently deletes messages from the replied message up to your command message.\n"
    "• no confirmation is shown.\n"
    "• works with or without a reason. example:\n"
    "<code>/spurge cleanup</code>\n\n"
    "<b>how to use:</b>\n"
    "→ reply to a message\n"
    "→ send /spurge or /spurge [reason]\n\n"
    "<b>limits:</b>\n"
    "• cannot delete messages older than ~48 hours.\n"
    "• you must be an admin or sudo user."
)


@app.on_message(filters.command("purgehelp"))
async def purge_help_command(client, message: Message):
    await message.reply(
        "<b>choose a command to view help:</b>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("purge", callback_data="purge_info"),
                InlineKeyboardButton("spurge", callback_data="spurge_info"),
            ],
            [InlineKeyboardButton("close", callback_data="purge_close")]
        ])
    )


@app.on_callback_query(filters.regex("purge_info"))
async def show_purge_info(client, query: CallbackQuery):
    await query.message.edit_text(
        PURGE_HELP,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("back", callback_data="purge_main")],
            [InlineKeyboardButton("close", callback_data="purge_close")]
        ])
    )


@app.on_callback_query(filters.regex("spurge_info"))
async def show_spurge_info(client, query: CallbackQuery):
    await query.message.edit_text(
        SPURGE_HELP,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("back", callback_data="purge_main")],
            [InlineKeyboardButton("close", callback_data="purge_close")]
        ])
    )


@app.on_callback_query(filters.regex("purge_main"))
async def show_main_buttons(client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>choose a command to view help:</b>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("purge", callback_data="purge_info"),
                InlineKeyboardButton("spurge", callback_data="spurge_info"),
            ],
            [InlineKeyboardButton("close", callback_data="purge_close")]
        ])
    )


@app.on_callback_query(filters.regex("purge_close"))
async def close_help_menu(client, query: CallbackQuery):
    await query.message.delete()