from asyncio import sleep
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check
from config import OWNER_ID


# Helper: split list into chunks of 100
def divide_chunks(lst, n=100):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def confirm_markup(cmd: str, user_id: int, from_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirmpurge|{cmd}|{user_id}|{from_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancelpurge")
        ]
    ])


@app.on_message(filters.command("purge") & filters.group)
async def purge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("Only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("Reply to a message to start purge.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("You're not an admin.")

    await message.reply(
        f"Delete messages from ID {message.reply_to_message.id} to {message.id}?",
        reply_markup=confirm_markup("purge", message.reply_to_message.id, message.from_user.id)
    )


@app.on_message(filters.command("spurge") & filters.group)
async def spurge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("Only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("Reply to a message to start spurge.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("You're not an admin.")

    await message.reply(
        f"Silently delete messages from ID {message.reply_to_message.id} to {message.id}?",
        reply_markup=confirm_markup("spurge", message.reply_to_message.id, message.from_user.id)
    )


@app.on_message(filters.command("del") & filters.group)
async def del_message(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("Only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("Reply to a message to delete it.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("You're not an admin.")

    try:
        await client.delete_messages(message.chat.id, [message.reply_to_message.id, message.id])
    except MessageDeleteForbidden:
        await message.reply("Can't delete message. Missing permissions.")
    except RPCError as e:
        await message.reply(f"Error: {e}")


@app.on_callback_query(filters.regex(r"^confirmpurge\|"))
async def confirm_purge(client, query: CallbackQuery):
    data = query.data.split("|")
    cmd, start_id, expected_uid, user_id = data[1], int(data[2]), int(data[3]), query.from_user.id

    if user_id != expected_uid:
        return await query.answer("Not your purge request.", show_alert=True)

    try:
        message = query.message
        end_id = message.reply_to_message.id if message.reply_to_message else message.id
        ids = list(range(start_id, end_id))

        for chunk in divide_chunks(ids):
            await client.delete_messages(chat_id=message.chat.id, message_ids=chunk, revoke=True)

        await message.edit_text(f"Deleted {len(ids)} messages.")
        await sleep(3)
        await message.delete()

    except MessageDeleteForbidden:
        await query.message.edit_text("Can't delete messages. Missing permissions.")
    except RPCError as e:
        await query.message.edit_text(f"Error: {e}")


@app.on_callback_query(filters.regex(r"^cancelpurge$"))
async def cancel_purge(client, query: CallbackQuery):
    await query.message.edit_text("Purge cancelled.")