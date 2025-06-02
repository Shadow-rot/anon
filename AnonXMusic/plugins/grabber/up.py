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
            photo=img_url,
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
        "img_url": img_url,
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


@app.on_message(filters.command("delete") & filters.user(SUDOERS))
async def delete_character(_, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.reply_text("Usage: /delete <ID>")

    char_id = args[1]
    character = await collection.find_one_and_delete({"id": char_id})
    if character:
        try:
            await app.delete_messages(LOGGER_ID, character["message_id"])
        except:
            pass
        await message.reply_text("✅ Character deleted.")
    else:
        await message.reply_text("❌ Character not found.")


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_character(_, message: Message):
    args = message.text.split(maxsplit=3)
    if len(args) != 4:
        return await message.reply_text("Usage: /update <ID> <field> <new_value>")

    char_id, field, new_value = args[1:]

    valid_fields = ["img_url", "name", "anime", "rarity"]
    if field not in valid_fields:
        return await message.reply_text(f"❌ Invalid field. Choose from: {', '.join(valid_fields)}")

    character = await collection.find_one({"id": char_id})
    if not character:
        return await message.reply_text("❌ Character not found.")

    if field == "name":
        new_value = new_value.replace("-", " ").title()
    elif field == "anime":
        new_value = new_value.replace("-", " ").title()
    elif field == "rarity":
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
            new_value = rarity_map[int(new_value)]
        except:
            return await message.reply_text("❌ Invalid rarity. Use 1 to 7.")

    await collection.update_one({"id": char_id}, {"$set": {field: new_value}})

    updated = await collection.find_one({"id": char_id})
    caption = (
        f"<b>Waifu Name:</b> {updated['name']}\n"
        f"<b>Anime Name:</b> {updated['anime']}\n"
        f"<b>Quality:</b> {updated['rarity']}\n"
        f"<b>ID:</b> {updated['id']}\n"
        f"Updated by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    )

    if field == "img_url":
        try:
            await app.delete_messages(LOGGER_ID, character["message_id"])
        except:
            pass
        msg = await app.send_photo(LOGGER_ID, photo=new_value, caption=caption)
        await collection.update_one({"id": char_id}, {"$set": {"message_id": msg.id}})
    else:
        try:
            await app.edit_message_caption(LOGGER_ID, character["message_id"], caption=caption)
        except:
            pass

    await message.reply_text("✅ Character updated.")