import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from AnonXMusic import app
from AnonXMusic.utils.jarvis_ban import admin_filter

spam_chats = []

@app.on_message(filters.command(["utag", "all", "mention", "@all"]) & filters.group & admin_filter)
async def tag_all_users(_, message): 
    replied = message.reply_to_message  
    if len(message.command) < 2 and not replied:
        return await message.reply_text("**Reply to a message or provide some text to tag everyone.**") 

    spam_chats.append(message.chat.id)      
    usernum = 0
    usertxt = ""

    text = ""
    if not replied and len(message.command) > 1:
        text = message.text.split(None, 1)[1]

    async for m in app.get_chat_members(message.chat.id): 
        if message.chat.id not in spam_chats:
            break

        if m.user.is_bot:
            continue  # Skip bots

        usernum += 1
        usertxt += f"\n⊚ {m.user.mention}"

        if usernum == 10:
            if replied:
                await replied.reply_text(usertxt, quote=True)
            else:
                await app.send_message(message.chat.id, f"{text}\n{usertxt}")
            await asyncio.sleep(2)
            usernum = 0
            usertxt = ""

    # Send remaining users if any
    if usertxt and message.chat.id in spam_chats:
        if replied:
            await replied.reply_text(usertxt, quote=True)
        else:
            await app.send_message(message.chat.id, f"{text}\n{usertxt}")

    try:
        spam_chats.remove(message.chat.id)
    except Exception:
        pass

@app.on_message(filters.command(["cancel", "ustop"]))
async def cancel_spam(client, message):
    if message.chat.id not in spam_chats:
        return await message.reply("𝐂𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐈'𝐦 𝐍𝐨𝐭 ..")

    is_admin = False
    try:
        participant = await client.get_chat_member(message.chat.id, message.from_user.id)
        if participant.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            is_admin = True
    except UserNotParticipant:
        pass

    if not is_admin:
        return await message.reply("𝐘𝐨𝐮 𝐀𝐫𝐞 𝐍𝐨𝐭 𝐀𝐝𝐦𝐢𝐧 𝐁𝐚𝐛𝐲")

    try:
        spam_chats.remove(message.chat.id)
    except Exception:
        pass
    return await message.reply("ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ....")