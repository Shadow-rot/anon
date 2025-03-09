import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.jarvis_ban import admin_filter

spam_chats = []

@app.on_message(filters.command(["utag", "all", "mention", "@all"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    if len(message.command) < 2 and not replied:
        return await message.reply_text("**Reply to a message or provide some text to tag everyone.**") 

    chat_id = message.chat.id
    if chat_id in spam_chats:
        return await message.reply_text("**Tagging is already in progress...**")

    spam_chats.append(chat_id)      
    usertxt = ""
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    async for member in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break

        user = member.user
        if user.is_bot:
            continue  # Skip bots

        usertxt += f"\n⊚ {user.mention}"

    # Send the full tag message
    try:
        if replied:
            await replied.reply_text(f"{text}\n{usertxt}", quote=True, disable_web_page_preview=True)
        else:
            await client.send_message(chat_id, f"{text}\n{usertxt}", disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text("**An error occurred while tagging.**")
    
    if chat_id in spam_chats:
        spam_chats.remove(chat_id)

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