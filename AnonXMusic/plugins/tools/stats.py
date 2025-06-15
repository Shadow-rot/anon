import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.__version__ import __version__ as pytgver

import config
from AnonXMusic import app
from AnonXMusic.core.userbot import assistants
from AnonXMusic.plugins import ALL_MODULES
from AnonXMusic.utils.database import get_served_chats, get_served_users, get_sudoers
from config import BANNED_USERS, OWNER_ID
from AnonXMusic.utils.mongo import mongodb

owner_filter = filters.user(OWNER_ID)


@app.on_message(filters.command(["stats", "gstats"]) & ~BANNED_USERS & owner_filter)
async def stats_cmd(client, message: Message):
    served_chats = await get_served_chats()
    served_users = await get_served_users()

    # Admin permission scan
    me = await app.get_me()
    admin_count = 0
    permission_counts = {
        "can_manage_chat": 0,
        "can_delete_messages": 0,
        "can_restrict_members": 0,
        "can_promote_members": 0,
        "can_invite_users": 0,
        "can_pin_messages": 0,
        "can_manage_video_chats": 0,
        "can_change_info": 0,
    }

    for chat in served_chats:
        chat_id = chat["chat_id"]
        try:
            member = await app.get_chat_member(chat_id, me.id)
            if member.status.name != "ADMINISTRATOR":
                continue
            perms = getattr(member, "privileges", None)
            if not perms:
                continue
            admin_count += 1
            for key in permission_counts:
                if getattr(perms, key, False):
                    permission_counts[key] += 1
        except:
            continue

    # System stats
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = f"{round(cpu_freq / 1000, 2)} GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)} MHz"
    except:
        cpu_freq = "Unavailable"

    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    used = hdd.used / (1024.0**3)
    free = hdd.free / (1024.0**3)

    call = await mongodb.command("dbstats")
    datasize = call["dataSize"] / 1024
    storage = call["storageSize"] / 1024

    text = f"""
<b>🧩 𝙱𝙾𝚃 𝚂𝚃𝙰𝚃𝚂:</b>
├─ 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍𝗌      : <code>{len(assistants)}</code>
├─ 𝖡𝖺𝗇𝗇𝖾𝖽 𝖴𝗌𝖾𝗋𝗌      : <code>{len(BANNED_USERS)}</code>
├─ 𝖢𝗁𝖺𝗍𝗌 𝖲𝖾𝗋𝗏𝖾𝖽     : <code>{len(served_chats)}</code>
├─ 𝖴𝗌𝖾𝗋𝗌 𝖲𝖾𝗋𝗏𝖾𝖽    : <code>{len(served_users)}</code>
├─ 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋𝗌       : <code>{len(await get_sudoers())}</code>
├─ 𝖬𝗈𝖽𝗎𝗅𝖾𝗌 𝖫𝗈𝖺𝖽𝖾𝖽    : <code>{len(ALL_MODULES)}</code>
├─ 𝖠𝗎𝗍𝗈 𝖫𝖾𝖺𝗏𝖾        : <code>{config.AUTO_LEAVING_ASSISTANT}</code>
└─ 𝖬𝖺𝗑 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇      : <code>{config.DURATION_LIMIT_MIN} min</code>

<b>🖥 𝙎𝙔𝙎𝙏𝙀𝙈 𝙎𝙏𝘼𝙏𝙎:</b>
├─ 𝖯𝗅𝖺𝗍𝖿𝗈𝗋𝗆         : <code>{platform.system()}</code>
├─ 𝖱𝖠𝖬              : <code>{ram}</code>
├─ 𝖢𝖯𝖴 𝖢𝗈𝗋𝖾𝗌        : <code>{p_core} Physical / {t_core} Total</code>
├─ 𝖢𝖯𝖴 𝖥𝗋𝖾𝗊𝗎𝖾𝗇𝖼𝗒    : <code>{cpu_freq}</code>
└─ 𝖧𝖣𝖣              : <code>{str(total)[:4]} GB • Used {str(used)[:4]} • Free {str(free)[:4]}</code>

<b>📦 𝙳𝙰𝚃𝙰𝙱𝙰𝚂𝙴:</b>
├─ 𝖣𝖠𝖳𝖠 𝖲𝗂𝗓𝖾         : <code>{str(datasize)[:6]} KB</code>
├─ 𝖲𝗍𝗈𝗋𝖺𝗀𝖾 𝖴𝗌𝖾𝖽     : <code>{str(storage)[:6]} KB</code>
├─ 𝖢𝗈𝗅𝗅𝖾𝖼𝗍𝗂𝗈𝗇𝗌       : <code>{call["collections"]}</code>
└─ 𝖣𝗈𝖼𝗎𝗆𝖾𝗇𝗍𝗌         : <code>{call["objects"]}</code>

<b>🛡 𝘼𝘿𝙈𝙄𝙉 𝘼𝘾𝘾𝙀𝙎𝙎:</b>
├─ 𝖠𝖽𝗆𝗂𝗇 𝖨𝗇         : <code>{admin_count} Chats</code>
├─ Manage Group     : <code>{permission_counts["can_manage_chat"]}</code>
├─ Delete Messages  : <code>{permission_counts["can_delete_messages"]}</code>
├─ Restrict Members : <code>{permission_counts["can_restrict_members"]}</code>
├─ Promote Members  : <code>{permission_counts["can_promote_members"]}</code>
├─ Invite Users     : <code>{permission_counts["can_invite_users"]}</code>
├─ Pin Messages     : <code>{permission_counts["can_pin_messages"]}</code>
├─ Video Chats      : <code>{permission_counts["can_manage_video_chats"]}</code>
└─ Change Info      : <code>{permission_counts["can_change_info"]}</code>
"""

    await message.reply_text(text.strip(), disable_web_page_preview=True)