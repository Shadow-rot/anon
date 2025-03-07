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

    # If replying to a message, use that message's text (without captions if media)
    if replied:
        if replied.text:
            tag_text = replied.text  # Use replied text
        else:
            tag_text = "tagging users below:"  # If it's media with no text
    else:
        if len(message.command) < 2:
            return await message.reply_text("reply to a message or provide text to tag all.") 
        tag_text = message.text.split(None, 1)[1]  # Use command text

    user_list = []
    async for m in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break  

        if not m.user or m.user.is_deleted:
            continue

        user_list.append(f"{m.user.mention}")

        if len(user_list) == 5:  # Send in batches of 5
            formatted_mentions = ", ".join(user_list)  
            if replied:
                await replied.reply_text(f"{tag_text}\n\n{formatted_mentions}")
            else:
                await message.reply_text(f"{tag_text}\n\n{formatted_mentions}")
            user_list.clear()
            await asyncio.sleep(2)  

    if user_list:
        formatted_mentions = ", ".join(user_list)  
        if replied:
            await replied.reply_text(f"{tag_text}\n\n{formatted_mentions}")
        else:
            await message.reply_text(f"{tag_text}\n\n{formatted_mentions}")

    spam_chats.discard(chat_id)  

@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_spam(client, message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply("currently not tagging anyone.")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("only admins can stop tagging.")
    except UserNotParticipant:
        return await message.reply("you are not a member of this group.")

    spam_chats.discard(chat_id)
    return await message.reply("tagging stopped.")