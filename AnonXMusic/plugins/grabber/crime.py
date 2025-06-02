from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument
from AnonXMusic import app
from AnonXMusic.utils.data import user_totals_collection

# SUDO USERS (change as needed)
SUDO_USER_IDS = {6507226414, 7938543259}

# /changetime (admin-only)
@app.on_message(filters.command("changetime") & filters.group)
async def change_time(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in ("administrator", "creator"):
            return await message.reply_text("You don't have permission to use this command.")

        args = message.text.split()
        if len(args) != 2 or not args[1].isdigit():
            return await message.reply_text("Incorrect format.\nUsage: `/changetime <number>`", quote=True)

        new_frequency = int(args[1])
        if new_frequency < 100:
            return await message.reply_text("Frequency must be at least 100.")
        if new_frequency > 10000:
            return await message.reply_text("That's too much. Use a value under 10000.")

        updated = await user_totals_collection.find_one_and_update(
            {"chat_id": str(chat_id)},
            {"$set": {"message_frequency": new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        await message.reply_text(f"✅ Frequency set to every `{new_frequency}` messages.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to change frequency.\nError: `{e}`")

# /ctime (sudo-only override)
@app.on_message(filters.command("ctime") & filters.group)
async def change_time_sudo(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        if user_id not in SUDO_USER_IDS:
            return await message.reply_text("You are not allowed to use this command.")

        args = message.text.split()
        if len(args) != 2 or not args[1].isdigit():
            return await message.reply_text("Incorrect format.\nUsage: `/ctime <number>`", quote=True)

        new_frequency = int(args[1])
        if new_frequency < 1:
            return await message.reply_text("Frequency must be at least 1.")
        if new_frequency > 10000:
            return await message.reply_text("That's too much. Use a value under 10000.")

        updated = await user_totals_collection.find_one_and_update(
            {"chat_id": str(chat_id)},
            {"$set": {"message_frequency": new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        await message.reply_text(f"✅ (SUDO) Frequency set to every `{new_frequency}` messages.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to change frequency.\nError: `{e}`")