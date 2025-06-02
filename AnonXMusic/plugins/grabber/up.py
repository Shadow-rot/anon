import urllib.request
from pyrogram import filters
from pyrogram.types import Message
from pymongo import ReturnDocument

from config import LOGGER_ID
from AnonXMusic import app
from AnonXMusic.utils.data import db, collection
from AnonXMusic.misc import SUDOERS


async def get_next_sequence_number(sequence_name: str) -> int:
    sequence_collection = db.sequences
    result = await sequence_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return result["sequence_value"]


@app.on_message(filters.command("upload") & filters.user(SUDOERS))
async def upload_character(_, message: Message):
    reply = message.reply_to_message

    if reply and reply.photo:
        args = message.text.split(maxsplit=3)
        if len(args) != 4:
            return await message.reply_text(
                "❌ Wrong format when replying to image!\n"
                "`/upload <character-name> <anime-name> <rarity>`\n\n"
                "Example:\n"
                "`/upload muzan-kibutsuji demon-slayer 3`\n\n"
                "Use rarity number accordingly:\n"
                "1:🟢 Common\n2:🔵 Medium\n3:🟡 Rare\n4:🔴 Legendary\n"
                "5:💠 Special\n6:🔮 Limited\n7:❄️ Winter"
            )
        name_raw, anime_raw, rarity_input = args[1:]
        image_url = await reply.download()
    else:
        args = message.text.split(maxsplit=4)
        if len(args) != 5:
            return await message.reply_text(
                "❌ Wrong format! Example:\n"
                "`/upload <Image_URL> <character-name> <anime-name> <rarity>`\n\n"
                "Example:\n"
                "`/upload https://files.catbox.moe/3joi8n.jpg muzan-kibutsuji demon-slayer 3`\n\n"
                "Use rarity number accordingly:\n"
                "1:🟢 Common\n2:🔵 Medium\n3:🟡 Rare\n4:🔴 Legendary\n"
                "5:💠 Special\n6:🔮 Limited\n7:❄️ Winter"
            )
        img_url, name_raw, anime_raw, rarity_input = args[1:]

        valid_exts = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        if not any(img_url.lower().endswith(ext) for ext in valid_exts):
            return await message.reply_text("❌ Invalid image URL. Must end with .jpg, .png, etc.")

        try:
            req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            urllib.request.urlopen(req)
        except Exception as e:
            return await message.reply_text(f"❌ Couldn't access image URL:\n{e}")

        image_url = img_url

    character_name = name_raw.replace("-", " ").title()
    anime = anime_raw.replace("-", " ").title()

    rarity_map = {
        1: "🟢 𝘾𝙤𝙢𝙢𝙤𝙣",
        2: "🔵 𝙈𝙚𝙙𝙞𝙪𝙢",
        3: "🟡 𝙍𝙖𝙧𝙚",
        4: "🔴 𝙇𝙚𝙜𝙚𝙣𝙙𝙖𝙧𝙮",
        5: "💠 𝙎𝙥𝙚𝙘𝙞𝙖𝙡",
        6: "🔮 𝙇𝙞𝙢𝙞𝙩𝙚𝙙",
        7: "❄️ 𝙒𝙞𝙣𝙩𝙚𝙧"
    }

    try:
        rarity = rarity_map[int(rarity_input)]
    except (KeyError, ValueError):
        return await message.reply_text("❌ Invalid rarity. Use numbers 1 to 7.")

    char_id = str(await get_next_sequence_number("character_id")).zfill(2)

    try:
        msg = await app.send_photo(
            LOGGER_ID,
            photo=image_url,
            caption=(
                f"<b>Waifu Name:</b> {character_name}\n"
                f"<b>Anime Name:</b> {anime}\n"
                f"<b>Quality:</b> {rarity}\n"
                f"<b>ID:</b> {char_id}\n"
                f"Added by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
            )
        )
    except Exception as e:
        return await message.reply_text(f"❌ Failed to send photo:\n{e}")

    await collection.insert_one({
        "id": char_id,
        "img_url": image_url,
        "name": character_name,
        "anime": anime,
        "rarity": rarity,
        "message_id": msg.id
    })

    await message.reply_text("✅ Waifu successfully uploaded!")


@app.on_message(filters.command("upload"))
async def no_access(_, message: Message):
    if message.from_user.id not in SUDOERS:
        await message.reply_text("🚫 Only my owner can upload waifus.")