import urllib.request
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import ReturnDocument

from config import LOGGER_ID as CHARA_CHANNEL_ID
from AnonXMusic import app
from AnonXMusic.utils.data import db, collection 
from AnonXMusic.misc import SUDOERS

async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']


@app.on_message(filters.command("upload") & filters.user(SUDOERS))
async def upload_character(_, message: Message):
    args = message.text.split(maxsplit=4)
    if len(args) != 5:
        return await message.reply_text("""
❌ Wrong format! Example:
`/upload <Image_URL> <character-name> <anime-name> <rarity>`

Example:
`/upload https://files.catbox.moe/3joi8n.jpg muzan-kibutsuji demon-slayer 3`

Use rarity number accordingly:
1:🟢 Common
2:🔵 Medium
3:🟡 Rare
4:🔴 Legendary
5:💠 Special
6:🔮 Limited
7:❄️ Winter
""")

    img_url, name_raw, anime_raw, rarity_input = args[1:]

    # Validate URL
    valid_exts = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    if not any(img_url.lower().endswith(ext) for ext in valid_exts):
        return await message.reply_text("❌ Invalid image URL. Must end with .jpg, .png, .webp, etc.")

    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlopen(req)
    except Exception as e:
        return await message.reply_text(f"❌ Couldn't access image URL:\n{e}")

    # Format inputs
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
        return await message.reply_text("❌ Invalid rarity. Use numbers from 1 to 7.")

    # Get next ID
    char_id = str(await get_next_sequence_number("character_id")).zfill(2)

    # Send photo to channel
    try:
        msg = await app.send_photo(
            CHARA_CHANNEL_ID,
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
        return await message.reply_text(f"❌ Failed to send photo: {e}")

    # Save to DB
    await collection.insert_one({
        "id": char_id,
        "img_url": img_url,
        "name": character_name,
        "anime": anime,
        "rarity": rarity,
        "message_id": msg.id
    })

    await message.reply_text("✅ Waifu successfully uploaded!")


# Non-sudo users fallback
@app.on_message(filters.command("upload"))
async def no_access(_, message: Message):
    if message.from_user.id not in SUDOERS:
        await message.reply_text("🚫 Only my owner can upload waifus.")

# /delete command
@app.on_message(filters.command("delete") & SUDOERS)
async def delete_character(_, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.reply_text("Usage: /delete ID")

    char_id = args[1]
    character = await collection.find_one_and_delete({"id": char_id})
    if character:
        try:
            await app.delete_messages(LOGGER_ID, character["message_id"])
        except:
            pass
        await message.reply_text("✅ Character deleted.")
    else:
        await message.reply_text("Character not found.")

# /update command
@app.on_message(filters.command("update") & SUDOERS)
async def update_character(_, message: Message):
    try:
        args = message.text.split(maxsplit=3)
        if len(args) != 4:
            return await message.reply_text("Usage: /update ID field new_value")

        char_id, field, new_value = args[1], args[2], args[3]
        valid_fields = ["img_url", "name", "anime", "rarity"]

        if field not in valid_fields:
            return await message.reply_text(f"Invalid field. Use one of: {', '.join(valid_fields)}")

        character = await collection.find_one({"id": char_id})
        if not character:
            return await message.reply_text("Character not found.")

        if field in ["name", "anime"]:
            new_value = new_value.replace("-", " ").title()
        elif field == "rarity":
            rarity_map = {
                1: "🟢 Common",
                2: "🔵 Medium",
                3: "🟡 Rare",
                4: "🔴 Legendary",
                5: "💠 Special",
                6: "🔮 Limited",
                7: "❄️ Winter",
            }
            try:
                new_value = rarity_map[int(new_value)]
            except:
                return await message.reply_text("Invalid rarity. Use 1-7 only.")

        await collection.update_one({"id": char_id}, {"$set": {field: new_value}})

        # Update caption or re-send if image changed
        if field == "img_url":
            try:
                await app.delete_messages(LOGGER_ID, character["message_id"])
            except:
                pass

            new_caption = (
                f"Character Name: {character.get('name') if field != 'name' else new_value}\n"
                f"Anime Name: {character.get('anime') if field != 'anime' else new_value}\n"
                f"Rarity: {character.get('rarity') if field != 'rarity' else new_value}\n"
                f"ID: {char_id}\n"
                f"Updated by: {message.from_user.mention}"
            )

            sent = await app.send_photo(LOGGER_ID, photo=new_value, caption=new_caption)
            await collection.update_one({"id": char_id}, {"$set": {"message_id": sent.id}})
        else:
            updated_character = await collection.find_one({"id": char_id})
            updated_caption = (
                f"Character Name: {updated_character['name']}\n"
                f"Anime Name: {updated_character['anime']}\n"
                f"Rarity: {updated_character['rarity']}\n"
                f"ID: {char_id}\n"
                f"Updated by: {message.from_user.mention}"
            )
            try:
                await app.edit_message_caption(
                    chat_id=LOGGER_ID,
                    message_id=character["message_id"],
                    caption=updated_caption
                )
            except:
                pass

        await message.reply_text("✅ Character updated.")
    except Exception as e:
        await message.reply_text(f"Error while updating.\n`{e}`")