from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from AnonXMusic import app
from AnonXMusic.core.call import Anony
from AnonXMusic.utils import bot_sys_stats
from AnonXMusic.utils.decorators.language import language
from AnonXMusic.utils.inline import supp_markup
from config import BANNED_USERS, OWNER_ID  # Make sure OWNER_ID is a list or set of ints


# Filter to allow only the owner
owner_filter = filters.user(OWNER_ID)


@app.on_message(filters.command(["ping", "alive",prefixes="/","."]) & ~BANNED_USERS & owner_filter)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_text(
        _["ping_1"].format(app.mention)
    )
    pytgping = await Anony.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping)
    )