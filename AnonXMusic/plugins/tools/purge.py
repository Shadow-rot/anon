from asyncio import sleep
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from AnonXMusic import app
from AnonXMusic.utils.admin_check import admin_check
from config import OWNER_ID


# Split list into chunks of 100
def divide_chunks(lst, n=100):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def confirm_markup(cmd: str, start_id: int, from_id: int, reason: str = ""):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirmpurge|{cmd}|{start_id}|{from_id}|{reason}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancelpurge")
        ]
    ])


@app.on_message(filters.command("purge") & filters.group)
async def purge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("❌ This command only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to a message to start purging.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("🔒 You're not an admin.")

    # Extract optional reason
    reason = " ".join(message.command[1:]) or "No reason provided"
    start_id = message.reply_to_message.id
    end_id = message.id
    count = abs(end_id - start_id)

    await message.reply(
        f"⚠️ Are you sure you want to delete **{count} messages** from ID `{start_id}` to `{end_id}`?\n\n"
        f"📝 Reason: `{reason}`",
        reply_markup=confirm_markup("purge", start_id, message.from_user.id, reason)
    )


@app.on_message(filters.command("spurge") & filters.group)
async def spurge_request(client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply("❌ This command only works in supergroups.")

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to a message to start silent purge.")

    is_admin = await admin_check(message)
    if message.from_user.id not in OWNER_ID and not is_admin:
        return await message.reply("🔒 You're not an admin.")

    reason = " ".join(message.command[1:]) or "No reason provided"
    start_id = message.reply_to_message.id
    end_id = message.id
    count = abs(end_id - start_id)

    await message.reply(
        f"⚠️ Silently delete **{count} messages** from ID `{start_id}` to `{end_id}`?\n"
        f"📝 Reason: `{reason}`",
        reply_markup=confirm_markup("spurge", start_id, message.from_user.id, reason)
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
        await message.reply("⚠️ Can't delete message. Missing permissions.")
    except RPCError as e:
        await message.reply(f"Error: {e}")


@app.on_callback_query(filters.regex(r"^confirmpurge\|"))
async def confirm_purge(client, query: CallbackQuery):
    data = query.data.split("|")
    cmd, start_id, expected_uid, reason = data[1], int(data[2]), int(data[3]), data[4]
    user_id = query.from_user.id

    if user_id != expected_uid:
        return await query.answer("This isn't your purge request.", show_alert=True)

    try:
        message = query.message
        end_id = message.reply_to_message.id if message.reply_to_message else message.id
        ids = list(range(start_id, end_id))

        deleted = 0
        for chunk in divide_chunks(ids):
            # Only delete messages not older than 2 days
            msgs = await client.get_messages(message.chat.id, chunk)
            deletable_ids = [msg.id for msg in msgs if msg and (datetime.utcnow() - msg.date) < timedelta(days=2)]

            if deletable_ids:
                await client.delete_messages(message.chat.id, deletable_ids, revoke=True)
                deleted += len(deletable_ids)

        await message.edit_text(
            f"✅ Purge completed. Deleted **{deleted} messages**.\n📝 Reason: `{reason}`"
        )
        await sleep(5)
        await message.delete()

    except MessageDeleteForbidden:
        await query.message.edit_text("⚠️ Can't delete messages. Missing permissions.")
    except RPCError as e:
        await query.message.edit_text(f"❌ Error: {e}")


@app.on_callback_query(filters.regex(r"^cancelpurge$"))
async def cancel_purge(client, query: CallbackQuery):
    await query.message.edit_text("❌ Purge cancelled.")


# ================== HELP COMMAND ==================

@app.on_message(filters.command("purgehelp"))
async def purge_help(client, message: Message):
    await message.reply(
        "**🧹 Purge Help Menu**\n\n"
        "`/purge [reason]` → Confirm before deleting messages from the replied message to yours.\n"
        "`/spurge [reason]` → Silent version of purge (no messages shown).\n"
        "`/del` → Delete a single replied message.\n\n"
        "**🔒 Access**: Admins or Bot Owner only.\n"
        "**📌 Notes:**\n"
        "• You can use optional reason like `/purge spam`.\n"
        "• Telegram restricts deletion of messages older than ~48 hours.\n"
        "• Confirmation required before purge to avoid mistakes.\n\n"
        "**Example:**\n"
        "`Reply to message`\n"
        "`/purge inappropriate content`\n\n"
        "🧠 Purge Smart. Purge Safe.",
        quote=True
    )