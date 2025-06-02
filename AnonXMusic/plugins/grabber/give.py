from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic.utils.data import (
    users_col as user_collection,
    collection  # character collection
)
from AnonXMusic import app
from AnonXMusic.misc import SUDOERS

DEV_LIST = [6507226414]  # Add more developer IDs as needed


# ✅ Give a character to a user
async def give_character(receiver_id: int, character_id: str):
    character = await collection.find_one({'id': character_id})
    if not character:
        raise ValueError("❌ Character not found.")

    try:
        await user_collection.update_one(
            {'id': receiver_id},
            {'$push': {'characters': character}},
            upsert=True
        )

        img_url = character.get('img_url', '')
        caption = (
            f"✅ Successfully Given To `{receiver_id}`\n"
            f"Information:\n"
            f"🎖️ Rarity: {character.get('rarity', 'N/A')}\n"
            f"📺 Anime: {character.get('anime', 'N/A')}\n"
            f"👤 Name: {character.get('name', 'N/A')}\n"
            f"🆔 ID: {character.get('id')}"
        )
        return img_url, caption
    except Exception as e:
        print(f"[ERROR] Failed to update user: {e}")
        raise


@app.on_message(filters.command("give") & filters.reply & filters.user(DEV_LIST))
async def give_character_command(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ You must reply to a user to give a character.")

    try:
        character_id = str(message.text.split()[1])
    except IndexError:
        return await message.reply("❗ Usage: /give <character_id> (reply to a user)")

    receiver_id = message.reply_to_message.from_user.id

    try:
        img_url, caption = await give_character(receiver_id, character_id)
        await message.reply_photo(photo=img_url, caption=caption, quote=True)
    except Exception as e:
        await message.reply(f"❌ {str(e)}", quote=True)


# ✅ Add all characters to a user's collection (used by dev)
async def add_all_characters_for_user(user_id: int) -> str:
    user = await user_collection.find_one({'id': user_id})
    if not user:
        return f"❌ User with ID `{user_id}` not found."

    all_characters = await collection.find({}).to_list(length=None)
    existing_ids = {char['id'] for char in user.get('characters', [])}
    new_characters = [char for char in all_characters if char['id'] not in existing_ids]

    if not new_characters:
        return f"✅ No new characters to add for user `{user_id}`"

    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': {'$each': new_characters}}}
    )
    return f"✅ Added {len(new_characters)} characters to user `{user_id}`."


@app.on_message(filters.command("add") & filters.user(DEV_LIST))
async def add_characters_command(client: Client, message: Message):
    user_id = message.from_user.id
    result = await add_all_characters_for_user(user_id)
    await message.reply(result, quote=True)


# ✅ Remove a character from a user's collection
async def kill_character(receiver_id: int, character_id: str) -> str:
    character = await collection.find_one({'id': character_id})
    if not character:
        raise ValueError("❌ Character not found.")

    try:
        await user_collection.update_one(
            {'id': receiver_id},
            {'$pull': {'characters': {'id': character_id}}}
        )
        return f"🗑️ Removed character `{character_id}` from user `{receiver_id}`."
    except Exception as e:
        print(f"[ERROR] Failed to remove character: {e}")
        raise


@app.on_message(filters.command("kill") & filters.reply & filters.user(DEV_LIST))
async def remove_character_command(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ You must reply to a user to remove a character.")

    try:
        character_id = str(message.text.split()[1])
    except IndexError:
        return await message.reply("❗ Usage: /kill <character_id> (reply to a user)")

    receiver_id = message.reply_to_message.from_user.id

    try:
        result = await kill_character(receiver_id, character_id)
        await message.reply(result, quote=True)
    except Exception as e:
        await message.reply(f"❌ {str(e)}", quote=True)