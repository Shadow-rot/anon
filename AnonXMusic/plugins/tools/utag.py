import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = set()  # Track ongoing tagging sessions

@app.on_message(filters.command(["utag", "all", "mention", "tagall"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    chat_id = message.chat.id

    if chat_id in spam_chats:
        return await message.reply_text("tagging is already in progress.") 

    if not replied:
        return await message.reply_text("reply to any message to tag all users on it.") 

    spam_chats.add(chat_id)

    # Get message caption or default text if available
    replied_text = replied.caption if replied.caption else "tagging users below:"
    user_list = []
    total_users = 0

    async for m in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break  

        if not m.user or m.user.is_deleted:
            continue

        user_list.append(f"{m.user.mention}")
        total_users += 1

        if len(user_list) == 5:  # Send in batches of 5
            formatted_mentions = ", ".join(user_list)  
            await replied.reply_text(f"{replied_text}\n\n{formatted_mentions}")
            user_list.clear()
            await asyncio.sleep(2)  

    if user_list:
        formatted_mentions = ", ".join(user_list)  
        await replied.reply_text(f"{replied_text}\n\n{formatted_mentions}")

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