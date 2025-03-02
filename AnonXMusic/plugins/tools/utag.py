"""import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPermissions
from AnonXMusic import app
from AnonXMusic.utils.shadwo_ban import admin_filter

spam_chats = []

@app.on_message(filters.command(["utag", "all", "mention"]) & filters.group & admin_filter)
async def tag_all_users(_,message): 
    replied = message.reply_to_message  
    if len(message.command) < 2 and not replied:
        await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ") 
        return                  
    if replied:
        spam_chats.append(message.chat.id)      
        usernum= 0
        usertxt = ""
        async for m in app.get_chat_members(message.chat.id): 
            if message.chat.id not in spam_chats:
                break       
            usernum += 5
            usertxt += f"\n⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"
            if usernum == 1:
                await replied.reply_text(usertxt)
                await asyncio.sleep(3)
                usernum = 0
                usertxt = ""
        try :
            spam_chats.remove(message.chat.id)
        except Exception:
            pass
    else:
        text = message.text.split(None, 1)[1]

        spam_chats.append(message.chat.id)
        usernum= 0
        usertxt = ""
        async for m in app.get_chat_members(message.chat.id):       
            if message.chat.id not in spam_chats:
                break 
            usernum += 1
            usertxt += f"\n⊚…"""