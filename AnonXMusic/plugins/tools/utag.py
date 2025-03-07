import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = set()  # Track active tagging sessions

@app.on_message(filters.command(["utag", "all", "mention", "tagall"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    chat_id = message.chat.id

    if chat_id in spam_chats:
        return await message.reply_text("tagging is already in progress.") 

    spam_chats.add(chat_id)

    # Get the tagging text
    tag_text = ""
    if replied:
        if replied.caption:  
            tag_text = replied.caption  # If it's a media file with a caption, use it
        elif replied.text:
            tag_text = replied.text  # If it's a text message, use its text
    else:
        tag_text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    if not tag_text:
        return await message.reply_text("reply to a message or provide a text to tag all.")

    user_list = []
    tagged_count = 0  # Count total tagged users

    async for m in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break  

        if not m.user or m.user.is_deleted:
            continue

        user_list.append(f"{m.user.mention}")
        tagged_count += 1  

        if len(user_list) == 5:  # Send in batches of 5
            formatted_mentions = ", ".join(user_list)  
            full_tag_msg = f"{tag_text}\n\n{formatted_mentions}"
            
            if replied:
                await replied.reply(full_tag_msg)  
            else:
                await message.reply_text(full_tag_msg)

            user_list.clear()
            await asyncio.sleep(2)  

    if user_list:
        formatted_mentions = ", ".join(user_list)  
        full_tag_msg = f"{tag_text}\n\n{formatted_mentions}"
        
        if replied:
            await replied.reply(full_tag_msg)  
        else:
            await message.reply_text(full_tag_msg)

    spam_chats.discard(chat_id)

    # ✅ Completion Message with User Count
    await message.reply_text(f"tagging completed! total users tagged: {tagged_count}")

@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_spam(client, message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply("ᴄᴜʀʀᴇɴᴛʟʏ I ᴀᴍ ɴᴏᴛ ᴛᴀɢɢɪɴɢ ᴀɴʏᴏɴᴇ.")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("ᴏɴʟʏ ᴀᴅᴍɪɴ ᴄᴀɴ sᴛᴏᴘ ᴛʜᴇ ᴛᴀɢɢɪɴɢ.")
    except UserNotParticipant:
        return await message.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ.")

    spam_chats.discard(chat_id)
    return await message.reply("ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ.")