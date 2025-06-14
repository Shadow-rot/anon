import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytgver

import config
from AnonXMusic import app
from AnonXMusic.core.userbot import assistants
from AnonXMusic.misc import SUDOERS, mongodb
from AnonXMusic.plugins import ALL_MODULES
from AnonXMusic.utils.database import get_served_chats, get_served_users, get_sudoers
from AnonXMusic.utils.decorators.language import language, languageCB
from AnonXMusic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS, OWNER_ID

owner_filter = filters.user(OWNER_ID)


@app.on_message(filters.command(["stats", "gstats"]) & ~BANNED_USERS & owner_filter)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, True)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS & owner_filter)
@languageCB
async def home_stats(client, CallbackQuery, _):
    upl = stats_buttons(_, True)
    await CallbackQuery.edit_message_text(
        text=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS & owner_filter)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await CallbackQuery.answer()
    upl = back_stats_buttons(_)

    served_chats = await get_served_chats()
    served_chats_count = len(served_chats)
    served_users = len(await get_served_users())

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
    labels = {
        "can_manage_chat": "Manage Group",
        "can_delete_messages": "Delete Msgs",
        "can_restrict_members": "Ban Users",
        "can_promote_members": "Promote",
        "can_invite_users": "Invite",
        "can_pin_messages": "Pin Msgs",
        "can_manage_video_chats": "Video Chats",
        "can_change_info": "Change Info",
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
        except Exception:
            continue

    # Main bot stats text
    base_text = _["gstats_3"].format(
        app.mention,
        len(assistants),
        len(BANNED_USERS),
        served_chats_count,
        served_users,
        len(ALL_MODULES),
        len(SUDOERS),
        config.AUTO_LEAVING_ASSISTANT,
        config.DURATION_LIMIT_MIN,
    )

    # Permissions text
    perm_text = "\n<b>Group Permissions Report</b>\n"
    perm_text += f"<b>Total Admin Groups:</b> <code>{admin_count}</code>\n"
    for key, label in labels.items():
        perm_text += f"<b>{label}:</b> <code>{permission_counts[key]}</code>\n"

    full_text = f"{base_text}\n{perm_text}"
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=full_text)

    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=full_text, reply_markup=upl
        )


@app.on_callback_query(filters.regex("bot_stats_sudo") & owner_filter)
@languageCB
async def bot_stats(client, CallbackQuery, _):
    upl = back_stats_buttons(_)
    await CallbackQuery.answer()
    await CallbackQuery.edit_message_text(_["gstats_1"].format(app.mention))

    # System info
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " ɢʙ"
    try:
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = (
            f"{round(cpu_freq / 1000, 2)}ɢʜᴢ" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)}ᴍʜᴢ"
        )
    except:
        cpu_freq = "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ"

    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    used = hdd.used / (1024.0**3)
    free = hdd.free / (1024.0**3)

    call = await mongodb.command("dbstats")
    datasize = call["dataSize"] / 1024
    storage = call["storageSize"] / 1024

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())

    text = _["gstats_5"].format(
        app.mention,
        len(ALL_MODULES),
        platform.system(),
        ram,
        p_core,
        t_core,
        cpu_freq,
        pyver.split()[0],
        pyrover,
        pytgver,
        str(total)[:4],
        str(used)[:4],
        str(free)[:4],
        served_chats,
        served_users,
        len(BANNED_USERS),
        len(await get_sudoers()),
        str(datasize)[:6],
        storage,
        call["collections"],
        call["objects"],
    )

    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )