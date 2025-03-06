import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = set()  # Using a set for better performance

@app.on_message(filters.command(["utag", "all", "mention", "@all"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    if len(message.command) < 2 and not replied:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ") 
    
    chat_id = message.chat.id
    if chat_id in spam_chats:
        return await message.reply_text("ᴛᴀɢɢɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss.") 

    spam_chats.add(chat_id)
    
    user_list = []
    async for m in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break  
        user_list.append(f"⊚ {m.user.mention}")
        
        if len(user_list) == 5:
            msg_text = replied.text if replied else message.text.split(None, 1)[1]
            await message.reply_text(f"{msg_text}\n\n" + "\n".join(user_list))
            user_list.clear()
            await asyncio.sleep(3)  # Prevent API flood

    spam_chats.discard(chat_id)

@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_spam(client, message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply("𝐂𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐈'𝐦 𝐍𝐨𝐭 𝐓𝐚𝐠𝐠𝐢𝐧𝐠.")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.")
    except UserNotParticipant:
        return await message.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴘᴀʀᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴘ.")

    spam_chats.discard(chat_id)
    return await message.reply("🦋 ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ.")