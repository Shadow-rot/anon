import asyncio
import random

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory

from AnonXMusic import userbot as us, app
from AnonXMusic.core.userbot import assistants


@app.on_message(filters.command("sg"))
async def sg(client: Client, message: Message):
    if not message.reply_to_message and len(message.text.split()) < 2:
        return await message.reply("**Usage:** Reply to a user or use `/sg username_or_id`")

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user.id
    else:
        target_user = message.text.split(None, 1)[1]

    lol = await message.reply("👀")

    try:
        user = await client.get_users(target_user)
    except Exception:
        return await lol.edit("<code>Please specify a valid user!</code>")

    sg_bots = ["sangmata_bot", "sangmata_beta_bot"]
    sg_bot = random.choice(sg_bots)

    ubot = assistants.get(1)
    if not ubot:
        return await lol.edit("Userbot not found or not connected.")

    try:
        send = await ubot.send_message(sg_bot, str(user.id))
        await send.delete()
    except Exception as e:
        return await lol.edit(f"Error contacting SangMata: `{e}`")

    await asyncio.sleep(1)

    found = False
    async for stalk in ubot.search_messages(sg_bot):
        if stalk.text:
            await message.reply(f"{stalk.text}")
            found = True
            break

    if not found:
        await message.reply("No results or bot may be down.")

    try:
        peer = await ubot.resolve_peer(sg_bot)
        await ubot.send(DeleteHistory(peer=peer, max_id=0, revoke=True))
    except Exception:
        pass

    await lol.delete()