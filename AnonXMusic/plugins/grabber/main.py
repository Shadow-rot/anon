import asyncio
import random
import re
import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from AnonXMusic.utils.data import (
    collection,
    top_global_groups_collection,
    group_user_totals_collection,
    users_col,  # changed here
)
from AnonXMusic import app  # your Pyrogram Client instance
from config import LOGGER_ID
from AnonXMusic.plugins.grabber import ALL_MODULES

locks = {}
last_user = {}
warned_users = {}
message_counts = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}

# Dynamically import all modules from grabber
import importlib
for module_name in ALL_MODULES:
    importlib.import_module(f"AnonXMusic.plugins.grabber.{module_name}")


def escape_markdown(text: str) -> str:
    escape_chars = r'*_`\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


@app.on_message(filters.group)
async def message_counter(client: Client, message: Message):
    chat_id = str(message.chat.id)
    user_id = message.from_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        chat_freq_doc = await group_user_totals_collection.find_one({'chat_id': chat_id})
        message_frequency = chat_freq_doc.get('message_frequency', 100) if chat_freq_doc else 100

        # Spam detection: If user sends 10+ messages in a row, warn and ignore for 10 mins
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    await message.reply_text(
                        f"⚠️ Don't spam, {message.from_user.first_name}.\n"
                        "Your messages will be ignored for 10 minutes."
                    )
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

        if message_counts[chat_id] % message_frequency == 0:
            await send_image(client, message)
            message_counts[chat_id] = 0


async def send_image(client: Client, message: Message):
    chat_id = message.chat.id

    all_characters = await collection.find({}).to_list(length=None)

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # Reset if all characters sent
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Pick character not sent yet
    available = [c for c in all_characters if c['id'] not in sent_characters[chat_id]]
    if not available:
        return
    character = random.choice(available)

    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    caption = (
        f"Guess this character:\n"
        f"Anime: {character.get('anime', 'Unknown')}\n"
        f"Hint: {character.get('hint', 'No hint')}"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("More Info", url=character.get('url', 'https://t.me/siyaprobot'))]]
    )

    # Send photo with caption but no parse_mode
    await client.send_photo(
        chat_id,
        photo=character.get('image', ''),
        caption=caption,
        reply_markup=buttons,
    )


@app.on_message(filters.group & filters.text)
async def guess_character(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip().lower()

    # If no character sent in chat, ignore
    if chat_id not in last_characters:
        return

    character = last_characters[chat_id]
    correct_answers = [ans.lower() for ans in character.get('name', '').split(",")]

    if text in correct_answers:
        if chat_id in first_correct_guesses:
            # Already guessed, ignore
            return
        else:
            first_correct_guesses[chat_id] = user_id

            await message.reply_text(
                f"🎉 Correct! {message.from_user.first_name} guessed the character: {character.get('name')}"
            )

            # Optionally, update user score in users_col collection here
            # Example:
            await users_col.update_one(
                {'user_id': user_id},
                {'$inc': {'score': 1}},
                upsert=True
            )

            # Remove last character so next round can start fresh
            last_characters.pop(chat_id, None)
            sent_characters[chat_id].remove(character['id'])


if __name__ == "__main__":
    print("AnonXMusic Grabber bot plugin started.")