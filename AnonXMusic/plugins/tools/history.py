import asyncio
import random

from pyrogram import Client, filters
from pyrogram.raw.functions.messages import DeleteHistory
from pyrogram.types import Message

from AnonXMusic import app
from AnonXMusic.core.userbot import assistants
from AnonXMusic.utils.database import get_client


@app.on_message(filters.command(["sg", "History"]))
async def sg(client: Client, message: Message):

    if len(message.text.split()) < 2 and not message.reply_to_message:
        return await message.reply("sg username/id/reply")
    if message.reply_to_message:
        args = message.reply_to_message.from_user.id
    else:
        args = message.text.split()[1:]
        if not args:
            return await message.reply(
                "Please provide a username, ID, or reply to a message."
            )
        args = args[0]
    lol = await message.reply("<code>Processing...</code>")
    if args:
        try:
            user = await client.get_users(f"{args}")
        except Exception:
            return await lol.edit("<code>Please specify a valid user!</code>")
    sgbot = ["sangmata_bot", "sangmata_beta_bot"]
    sg = random.choice(sgbot)
    VIP = random.choice(assistants)
    ubot = await get_client(VIP)

    try:
        a = await ubot.send_message(sg, f"{user.id}")
        await a.delete()
    except Exception as e:
        return await lol.edit(str(e))
    await asyncio.sleep(1)

    async for stalk in ubot.search_messages(a.chat.id):
        if stalk.text is None:
            continue
        if not stalk:
            await message.reply("botnya ngambek")
        elif stalk:
            await message.reply(f"{stalk.text}")
            break

    try:
        user_info = await ubot.resolve_peer(sg)
        await ubot.send(DeleteHistory(peer=user_info, max_id=0, revoke=True))
    except Exception:
        pass

    await lol.delete()


__MODULE__ = "Hɪsᴛᴏʀʏ"
__HELP__ = """
## Hɪsᴛᴏʀʏ Cᴏᴍᴍᴀɴᴅs Hᴇᴘ

### 1. /sɢ ᴏʀ /Hɪsᴛᴏʀʏ
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Fᴇᴛᴄʜᴇs ᴀ ʀᴀɴᴅᴏᴍ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ʜɪsᴛᴏʀʏ.

**Usᴀɢᴇ:**
/sɢ [ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ/ʀᴇᴘʏ]

**Dᴇᴛᴀɪs:**
- Fᴇᴛᴄʜᴇs ᴀ ʀᴀɴᴅᴏᴍ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʜɪsᴛᴏʀʏ ᴏғ ᴛʜᴇ sᴘᴇᴄɪғɪᴇᴅ ᴜsᴇʀ.
- Cᴀɴ ʙᴇ ᴜsᴇᴅ ʙʏ ᴘʀᴏᴠɪᴅɪɴɢ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ᴜsᴇʀ ID, ᴏʀ ʀᴇᴘʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ᴜsᴇʀ.
- Aᴄᴄᴇssɪʙᴇ ᴏɴʏ ʙʏ ᴛʜᴇ ʙᴏᴛ's ᴀssɪsᴛᴀɴᴛs.

**Exᴀᴍᴘᴇs:**
- `/sɢ ᴜsᴇʀɴᴀᴍᴇ`
- `/sɢ ᴜsᴇʀ_ɪᴅ`
- `/sɢ [ʀᴇᴘʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]`
"""