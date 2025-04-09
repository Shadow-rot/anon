import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic import app
from config import OWNER_ID

# Dictionary to store VC start times per chat
vc_start_times = {}

@app.on_message(filters.video_chat_started)
async def brah(_, msg):
    chat_id = msg.chat.id
    vc_start_times[chat_id] = datetime.datetime.now()
    await msg.reply("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ")

@app.on_message(filters.video_chat_ended)
async def brah2(_, msg):
    chat_id = msg.chat.id
    start_time = vc_start_times.pop(chat_id, None)
    if start_time:
        duration = datetime.datetime.now() - start_time
        seconds = duration.total_seconds()
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours}h {minutes}m {seconds}s"
        await msg.reply(f"ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ\nᴅᴜʀᴀᴛɪᴏɴ: {time_str}")
    else:
        await msg.reply("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ\nᴅᴜʀᴀᴛɪᴏɴ: ᴜɴᴋɴᴏᴡɴ")

@app.on_message(filters.video_chat_members_invited)
async def brah3(app: Client, message: Message):
    text = f"{message.from_user.mention} ɪɴᴠɪᴛᴇᴅ "
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f"{user.mention} "
            x += 1
        except Exception:
            pass
    try:
        await message.reply(f"{text} 😉")
    except:
        pass

@app.on_message(filters.command("math", prefixes="/"))
def calculate_math(client, message):   
    expression = message.text.split("/math ", 1)[1]
    try:        
        result = eval(expression)
        response = f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : {result}"
    except:
        response = "ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"
    message.reply(response)

@app.on_message(filters.command("leavegroup") & filters.user(OWNER_ID))
async def bot_leave(_, message):
    chat_id = message.chat.id
    text = f"sᴜᴄᴄᴇssғᴜʟʟʏ   ʟᴇғᴛ  !!."
    await message.reply_text(text)
    await app.leave_chat(chat_id=chat_id, delete=True)