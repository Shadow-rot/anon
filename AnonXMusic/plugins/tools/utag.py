import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = set()  # Track ongoing tagging sessions

def to_small_caps(text):
    """Convert text to small caps."""
    normal = "abcdefghijklmnopqrstuvwxyz"
    small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    translation_table = str.maketrans(normal, small_caps)
    return text.translate(translation_table)

@app.on_message(filters.command(["utag", "all", "mention", "tagall"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    chat_id = message.chat.id

    # Check if tagging is already in progress
    if chat_id in spam_chats:
        return await message.reply_text("tagging is already in progress.") 

    # Ensure a replied message exists
    if not replied or not replied.text:
        return await message.reply_text("reply to a message to tag all users on that message.") 

    spam_chats.add(chat_id)  # Mark chat as currently tagging

    # Convert replied message text to small caps
    replied_text = to_small_caps(replied.text)

    user_list = []
    total_users = 0

    async for m in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break  
        
        # Skip deleted accounts
        if not m.user or m.user.is_deleted:
            continue

        user_list.append(f"{m.user.mention}")
        total_users += 1

        if len(user_list) == 5:  # Send in batches of 5
            formatted_mentions = " | ".join(user_list)  
            await replied.reply_text(f"{replied_text}\n\n{formatted_mentions}")
            user_list.clear()
            await asyncio.sleep(2)  # Prevent API flood

    # Send remaining users (if any)
    if user_list:
        formatted_mentions = " | ".join(user_list)  
        await replied.reply_text(f"{replied_text}\n\n{formatted_mentions}")

    spam_chats.discard(chat_id)  # Remove from active tagging list
    await message.reply_text(f"finished tagging {total_users} users.")

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
    return await message.reply("tagging stopped successfully.")