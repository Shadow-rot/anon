import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = []

@app.on_message(filters.command(["utag", "all", "mention", "@all", "atag", "@alltag"]) & filters.group & admin_filter)
async def tag_all_users(client, message):
    chat_id = message.chat.id

    if chat_id in spam_chats:
        return await message.reply("**Tagging is already in progress...**")

    spam_chats.append(chat_id)

    replied = message.reply_to_message
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    batch = []
    count = 0

    try:
        members = client.get_chat_members(chat_id)
        async for member in members:
            if chat_id not in spam_chats:
                break

            user = member.user

            # Skip bots and deleted accounts
            if user.is_bot or user.is_deleted:
                continue

            username = user.username
            if username:
                mention = f"⊚ @{username}"
            else:
                mention = f"⊚ {user.mention}"

            batch.append(mention)
            count += 1

            if count % 10 == 0:
                await send_batch(client, chat_id, replied, text, batch)
                batch = []
                await asyncio.sleep(2)

        if batch and chat_id in spam_chats:
            await send_batch(client, chat_id, replied, text, batch)

    finally:
        if chat_id in spam_chats:
            spam_chats.remove(chat_id)

async def send_batch(client, chat_id, replied, text, batch):
    tag_text = f"{text}\n" + "\n".join(batch)
    try:
        if replied:
            await replied.reply_text(tag_text, quote=True, disable_web_page_preview=True)
        else:
            await client.send_message(chat_id, tag_text, disable_web_page_preview=True)
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        await send_batch(client, chat_id, replied, text, batch)
    except Exception as e:
        print(f"Error while tagging: {e}")

@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_spam(client, message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply("**No ongoing tagging right now.**")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return await message.reply("**You must be an admin to stop tagging.**")
    except UserNotParticipant:
        return await message.reply("**You must be in the group to stop tagging.**")

    spam_chats.remove(chat_id)
    return await message.reply("**Tagging has been stopped.**")

# NEW: Message-based "@" trigger
@app.on_message(filters.group & filters.text & admin_filter)
async def tag_on_at_symbol(client, message):
    if not message.text.strip().lower().startswith("@"):
        return

    # Simulate a command for the tag_all_users function
    message.command = ["@all"]
    await tag_all_users(client, message)