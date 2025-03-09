import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = set()

@app.on_message(filters.command(["utag", "all", "mention", "tagall"]) & filters.group & admin_filter)
async def tag_all_users(client, message): 
    replied = message.reply_to_message  
    chat_id = message.chat.id

    if chat_id in spam_chats:
        return await message.reply_text("ᴛᴀɢɢɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ɢᴏɪɴɢ ᴏɴ......") 

    spam_chats.add(chat_id)

    # Get tagging text
    tag_text = ""
    if replied:
        tag_text = replied.caption or replied.text or "➤"
    else:
        tag_text = message.text.split(None, 1)[1] if len(message.command) > 1 else "➤"

    user_list = []
    tagged_count = 0

    async for m in client.get_chat_members(chat_id): 
        if chat_id not in spam_chats:
            break  # Tagging was cancelled

        if not m.user or m.user.is_deleted or m.user.is_bot:
            continue

        user_list.append(m.user.mention)
        tagged_count += 1  

        if len(user_list) == 10:
            full_tag_msg = f"{tag_text}\n\n{', '.join(user_list)}"
            try:
                if replied:
                    await replied.reply(full_tag_msg)
                else:
                    await message.reply_text(full_tag_msg)
            except:
                pass
            user_list.clear()
            await asyncio.sleep(1.5)

    if user_list and chat_id in spam_chats:
        full_tag_msg = f"{tag_text}\n\n{', '.join(user_list)}"
        try:
            if replied:
                await replied.reply(full_tag_msg)
            else:
                await message.reply_text(full_tag_msg)
        except:
            pass

    spam_chats.discard(chat_id)
    await message.reply_text(f"✅ ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.\n👤 ᴛᴏᴛᴀʟ ᴜsᴇʀs ᴛᴀɢɢᴇᴅ: {tagged_count}")

@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_spam(client, message):
    chat_id = message.chat.id
    if chat_id not in spam_chats:
        return await message.reply("Currently not tagging anyone.")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("Only admins can stop tagging.")
    except UserNotParticipant:
        return await message.reply("You're not a member of this group.")

    spam_chats.discard(chat_id)
    return await message.reply("✅ Tagging stopped.")