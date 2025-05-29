"""
from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from cachetools import TTLCache
from pymongo import ASCENDING
from html import escape
import re

from AnonXMusic import app
from AnonXMusic.utils.harem_db import harem_collection as collection, harem_users as user_collection, db

# MongoDB indexes
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])
db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

# Caches
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

@app.on_inline_query()
async def inlinequery(client, query: types.InlineQuery):
    offset = int(query.offset) if query.offset else 0

    if query.query.startswith('collection.'):
        parts = query.query.split(' ')
        user_id = parts[0].split('.')[1]
        search_terms = ' '.join(parts[1:])

        if user_id.isdigit():
            if user_id in user_collection_cache:
                user = user_collection_cache[user_id]
            else:
                user = await user_collection.find_one({'id': int(user_id)})
                user_collection_cache[user_id] = user

            if user:
                all_characters = list({v['id']: v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(search_terms, re.IGNORECASE)
                    all_characters = [
                        character for character in all_characters
                        if regex.search(character['name']) or regex.search(character['anime'])
                    ]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        if query.query:
            regex = re.compile(query.query, re.IGNORECASE)
            all_characters = await collection.find({
                "$or": [{"name": regex}, {"anime": regex}]
            }).to_list(length=None)
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = await collection.find({}).to_list(length=None)
                all_characters_cache['all_characters'] = all_characters

    characters = all_characters[offset:offset+50]
    next_offset = str(offset + len(characters)) if len(characters) == 50 else ""

    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])

            caption = (
                f"<b>Look At <a href='tg://user?id={user['id']}'>{escape(user.get('first_name', str(user['id'])))}</a>'s Character</b>\n\n"
                f"🌸: <b>{character['name']} (x{user_character_count})</b>\n"
                f"🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n"
                f"<b>{character['rarity']}</b>\n\n"
                f"<b>🆔️:</b> {character['id']}"
            )
        else:
            caption = (
                f"<b>Look At This Character !!</b>\n\n"
                f"🌸: <b>{character['name']}</b>\n"
                f"🏖️: <b>{character['anime']}</b>\n"
                f"<b>{character['rarity']}</b>\n"
                f"🆔️: <b>{character['id']}</b>\n\n"
                f"<b>Globally Guessed {global_count} Times...</b>"
            )

        results.append(
            types.InlineQueryResultPhoto(
                title=character['name'],
                thumb_url=character['img_url'],
                photo_url=character['img_url'],
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
        )

    await client.answer_inline_query(
        query.id,
        results=results,
        next_offset=next_offset,
        cache_time=5,
        is_gallery=True
    )
"""