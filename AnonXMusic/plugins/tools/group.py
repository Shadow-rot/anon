import datetime
import ast
from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic import app
from config import OWNER_ID

vc_start_times = {}

def smallcaps(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ" * 2
    return text.translate(str.maketrans(normal, small))

@app.on_message(filters.video_chat_started)
async def on_vc_start(_, message: Message):
    await message.reply(smallcaps("voice chat started"))

@app.on_message(filters.video_chat_ended)
async def on_vc_end(_, message: Message):
    chat_id = message.chat.id
    start_time = vc_start_times.pop(chat_id, None)

    if start_time:
        duration = datetime.datetime.utcnow() - start_time
        total = int(duration.total_seconds())
        h, r = divmod(total, 3600)
        m, s = divmod(r, 60)

        duration_str = f"{h}h {m}m {s}s"
        await message.reply(smallcaps(f"voice chat ended\nDuration: {duration_str}"))
    else:
        await message.reply(smallcaps("voice chat ended\nDuration: unknown"))

@app.on_message(filters.video_chat_members_invited)
async def on_vc_invite(_, message: Message):
    inviter = message.from_user.mention if message.from_user else "Someone"
    invited = ", ".join([u.mention for u in message.video_chat_members_invited.users if u])
    await message.reply(smallcaps(f"{inviter} invited: {invited}"))

@app.on_message(filters.command("math"))
async def math_solver(_, message: Message):
    if len(message.command) < 2:
        return await message.reply(smallcaps("send a valid expression like: /math 2 + 2"))

    expression = message.text.split(maxsplit=1)[1]

    try:
        node = ast.parse(expression, mode="eval")
        for subnode in ast.walk(node):
            if not isinstance(subnode, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.operator, ast.unaryop)):
                raise ValueError("Unsafe expression")
        result = eval(compile(node, "<string>", "eval"))
        await message.reply(smallcaps(f"result: {result}"))
    except Exception:
        await message.reply(smallcaps("invalid expression or unsafe input"))

@app.on_message(filters.command("leavegroup") & filters.user(OWNER_ID))
async def leave_group(_, message: Message):
    try:
        await message.reply(smallcaps("leaving group..."))
        await app.leave_chat(message.chat.id, delete=True)
    except Exception as e:
        await message.reply(smallcaps(f"failed to leave:\n{e}"))