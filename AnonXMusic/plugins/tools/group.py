import datetime
import ast
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app
from config import OWNER_ID

# MongoDB setup
mongo_url = "mongodb+srv://Sha:u8KqYML48zhyeWB@cluster0.ebq5nwm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(mongo_url)
db = mongo_client["AnonXMusic"]
vc_collection = db["vc_stats"]

# Small caps converter
def smallcaps(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ" * 2
    return text.translate(str.maketrans(normal, small))

# Track VC start time
vc_start_times = {}

@app.on_message(filters.video_chat_started)
async def on_vc_start(client, message: Message):
    chat_id = message.chat.id
    chat = message.chat
    vc_start_times[chat_id] = datetime.datetime.utcnow()

    # Notify Owner
    notify_text = (
        f"<b>🎙️ Voice Chat Started</b>\n\n"
        f"<b>Group:</b> {chat.title}\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>\n"
        f"<b>Username:</b> @{chat.username if chat.username else 'N/A'}\n\n"
        f"<i>Auto alert from VC tracker</i>"
    )
    try:
        await client.send_message(OWNER_ID, notify_text)
    except Exception as e:
        print(f"[VC Notify] Error: {e}")

    await message.reply(smallcaps("Voice chat started."))

@app.on_message(filters.video_chat_ended)
async def on_vc_end(_, message: Message):
    chat_id = message.chat.id
    start_time = vc_start_times.pop(chat_id, None)

    if start_time:
        duration = datetime.datetime.utcnow() - start_time
        total_sec = int(duration.total_seconds())
        h, r = divmod(total_sec, 3600)
        m, s = divmod(r, 60)
        duration_str = f"{h}h {m}m {s}s"

        vc_collection.insert_one({
            "chat_id": chat_id,
            "title": message.chat.title,
            "ended_at": datetime.datetime.utcnow(),
            "duration_seconds": total_sec,
            "duration_str": duration_str,
        })

        await message.reply(smallcaps(f"Voice chat ended.\nDuration: {duration_str}"))
    else:
        await message.reply(smallcaps("Voice chat ended.\nDuration: unknown"))

@app.on_message(filters.video_chat_members_invited)
async def on_vc_invite(_, message: Message):
    inviter = message.from_user.mention if message.from_user else "Someone"
    invited = ", ".join([u.mention for u in message.video_chat_members_invited.users if u])
    await message.reply(smallcaps(f"{inviter} invited: {invited}"))

@app.on_message(filters.command("math"))
async def math_solver(_, message: Message):
    if len(message.command) < 2:
        return await message.reply(smallcaps("Send a valid expression like: /math 2 + 2"))

    expression = message.text.split(maxsplit=1)[1]
    try:
        node = ast.parse(expression, mode="eval")
        for sub in ast.walk(node):
            if not isinstance(sub, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.operator, ast.unaryop)):
                raise ValueError("Unsafe expression")
        result = eval(compile(node, "<string>", "eval"))
        await message.reply(smallcaps(f"Result: {result}"))
    except Exception:
        await message.reply(smallcaps("Invalid expression or unsafe input"))

@app.on_message(filters.command("leavegroup") & filters.user(OWNER_ID))
async def leave_group(_, message: Message):
    try:
        await message.reply(smallcaps("Leaving group..."))
        await app.leave_chat(message.chat.id, delete=True)
    except Exception as e:
        await message.reply(smallcaps(f"Failed to leave:\n{e}"))

@app.on_message(filters.command("vcstats") & filters.user(OWNER_ID))
async def vc_stats(_, message: Message):
    stats = vc_collection.find().sort("ended_at", -1).limit(10)
    text = smallcaps("Last 10 Voice Chat Sessions:\n\n")
    for doc in stats:
        text += (
            f"• {doc.get('title', 'Unknown Group')}\n"
            f"  - Duration: {doc['duration_str']}\n"
            f"  - Ended: {doc['ended_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
        )
    await message.reply(text or "No data yet.")