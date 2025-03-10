import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = []

@app.on_message(filters.command(["utag", "all", "mention", "@all"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    if len(message.command) < 2 and not replied:
        return await message.reply_text("Reply to a message or provide some text to tag everyone.") 

    chat_id = message.chat.id
    if chat_id in spam_chats:
        return await message.reply_text("Tagging is already in progress...")

    spam_chats.append(chat_id)      
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    batch = []
    count = 0

    async for member in client.get_chat_members(chat_id):
        if chat_id not in spam_chats:
            break

        user = member.user
        if user.is_bot:
            continue  # Skip bots, tag everyone else

        batch.append(f"⊚ {user.mention}")
        count += 1

        if count % 10 == 0:
            try:
                tag_text = f"{text}\n" + "\n".join(batch)
                if replied:
                    await replied.reply_text(tag_text, quote=True, disable_web_page_preview=True)
                else:
                    await message.reply_text(tag_text, disable_web_page_preview=True)
            except Exception:
                pass
            await asyncio.sleep(1)  # Delay reduced to 1 second
            batch = []

    # Send any remaining users
    if batch and chat_id in spam_chats:
        try:
            tag_text = f"{text}\n" + "\n".join(batch)
            if replied:
                await replied.reply_text(tag_text, quote=True, disable_web_page_preview=True)
            else:
                await message.reply_text(tag_text, disable_web_page_preview=True)
        except Exception:
            pass

    if chat_id in spam_chats:
        spam_chats.remove(chat_id)

@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_spam(client, message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply("No ongoing tagging right now.")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return await message.reply("You must be an admin to stop tagging.")
    except UserNotParticipant:
        return await message.reply("You must be in the group to stop tagging.")

    spam_chats.remove(chat_id)
    return await message.reply("Tagging has been stopped.")