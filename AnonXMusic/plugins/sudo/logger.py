from pyrogram import filters

from AnonXMusic import app
from config import OWNER_ID
from AnonXMusic.utils.database import add_off, add_on
from AnonXMusic.utils.decorators.language import language

only_owner = filters.user(OWNER_ID)

@app.on_message(filters.command(["logger"]) & only_owner)
@language
async def logger(client, message, _):
    usage = _["log_1"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip().lower()
    if state == "enable":
        await add_on(2)
        await message.reply_text(_["log_2"])
    elif state == "disable":
        await add_off(2)
        await message.reply_text(_["log_3"])
    else:
        await message.reply_text(usage)
