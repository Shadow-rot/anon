import asyncio
import random

from pyrogram import Client, filters
from pyrogram.types import Message

from AnonXMusic import app
from AnonXMusic.core.userbot import assistants
from AnonXMusic.utils.database import get_client


@app.on_message(filters.command(["sg", "History"]))
async def sg(client: Client, message: Message):

    if len(message.text.split()) < 2 and not message.reply_to_message:
        return await message.reply("Usage: /sg username/id/reply")
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        args = message.text.split()[1]
        try:
            user = await client.get_users(args)
            user_id = user.id
        except Exception:
            return await message.reply("<code>Invalid user provided!</code>")

    msg = await message.reply("<code>Processing...</code>")
    
    sgbots = ["sangmata_bot", "sangmata_beta_bot"]
    
    # Get a working assistant
    for _ in range(5):  # Try multiple assistants if one fails
        VIP = random.choice(assistants)
        try:
            ubot = await get_client(VIP)
            break
        except Exception:
            continue
    else:
        return await msg.edit("<code>No available assistants!</code>")

    try:
        while True:  # Infinite loop to keep checking until data is found
            sg_bot = random.choice(sgbots)
            request_msg = await ubot.send_message(sg_bot, str(user_id))
            await asyncio.sleep(2)  # Give some time for bot to respond

            async for stalk in ubot.search_messages(sg_bot):
                if stalk.text:
                    await message.reply(stalk.text)
                    return  # Exit function once message is found
            
            await request_msg.delete()  # Clean up old request messages before retrying
            await asyncio.sleep(2)  # Wait before retrying to avoid spam
            
    except Exception as e:
        return await msg.edit(f"Error: {e}")

    await msg.delete()


__MODULE__ = "Hɪsᴛᴏʀʏ"
__HELP__ = """
### /sg ᴏʀ /Hɪsᴛᴏʀʏ
Fetches username history.

**Usage:**
`/sg username/id/reply`
"""