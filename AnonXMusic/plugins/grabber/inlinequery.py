import re
from cachetools import TTLCache
from pymongo import ASCENDING
from pyrogram import Client, types
from AnonXMusic import app
from AnonXMusic.utils.data import users_col, collection, db

# Indexes for performance
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
async def inlinequery(client: Client, query: types.InlineQuery):
    offset = int(query.offset) if query.offset else 0
    all_characters = []

    # User collection mode
    if query.query.startswith('collection.'):
        parts = query.query.split(' ')
        first = parts[0].split('.')
        if len(first) < 2 or not first[1].isdigit():
            return  # malformed query

        user_id = first[1]
        search_terms = ' '.join(parts[1:])

        if user_id in user_collection_cache:
            user = user_collection_cache[user_id]
        else:
            user = await users_col.find_one({'id': int(user_id)})
            user_collection_cache[user_id] = user

        if user:
            all_characters = list({v['id']: v for v in user['characters']}.values())
            if search_terms:
                regex = re.compile(search_terms, re.IGNORECASE)
                all_characters = [
                    c for c in all_characters
                    if regex.search(c['name']) or regex.search(c['anime'])
                ]
    else:
        # Global search mode
        if query.query:
            regex = re.compile(query.query, re.IGNORECASE)
            all_characters = await collection.find({
                "$or": [
                    {"name": regex},
                    {"anime": regex}
                ]
            }).to_list(length=None)
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = await collection.find({}).to_list(length=None)
                all_characters_cache['all_characters'] = all_characters

    # Paginate
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + len(characters)) if len(characters) == 50 else ""

    results = []
    for character in characters:
        global_count = await users_col.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})
        total_characters = len(all_characters)

        if query.query.startswith('collection.'):
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = (
                f"Look At {(user.get('first_name') or user_id)}'s Character\n\n"
                f"🌸: {character['name']} (x{user_character_count})\n"
                f"🏖️: {character['anime']} ({user_anime_characters}/{anime_characters})\n"
                f"{character['rarity']}\n\n"
                f"🆔️: {character['id']}"
            )
        else:
            caption = (
                f"Look At This Character !!\n\n"
                f"🌸: {character['name']}\n"
                f"🏖️: {character['anime']}\n"
                f"{character['rarity']}\n"
                f"🆔️: {character['id']}\n\n"
                f"Globally Guessed {global_count} Times..."
            )

        results.append(
            types.InlineQueryResultPhoto(
                title=character['name'],
                thumb_url=character['img_url'],
                photo_url=character['img_url'],
                caption=caption
            )
        )

    # Only answer if results exist
    if results:
        await client.answer_inline_query(
            query.id,
            results=results,
            next_offset=next_offset,
            cache_time=5,
            is_gallery=True
        )
    else:
        await client.answer_inline_query(
            query.id,
            results=[],
            switch_pm_text="No results found!",
            switch_pm_parameter="start"
        )