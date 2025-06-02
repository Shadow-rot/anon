from pyrogram import filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InputMediaPhoto
)
from AnonXMusic import app
from AnonXMusic.utils.data import collection, users_col
from itertools import groupby
import math
import random

# /harem command
@app.on_message(filters.command("harem"))
async def harem_cmd(client, message: Message):
    await show_harem(client, message, message.from_user.id, 0)

# Callback handler for pagination
@app.on_callback_query(filters.regex(r"^harem:(\d+):(\d+)$"))
async def harem_callback(client, query: CallbackQuery):
    page, user_id = map(int, query.data.split(":")[1:])
    if query.from_user.id != user_id:
        await query.answer("This is not your harem!", show_alert=True)
        return
    await show_harem(client, query, user_id, page)

# Main harem rendering logic
async def show_harem(client, event, user_id: int, page: int = 0):
    user = await users_col.find_one({'id': user_id})
    if not user or "characters" not in user or not user["characters"]:
        text = "You have not grabbed any waifu yet..."
        if isinstance(event, Message):
            await event.reply(text)
        else:
            await event.edit_message_text(text)
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    unique_characters = list({c['id']: c for c in characters}.values())

    total_pages = max(1, math.ceil(len(unique_characters) / 7))
    page = max(0, min(page, total_pages - 1))

    harem_msg = f"{event.from_user.first_name}'s Harem - Page {page + 1}/{total_pages}\n"
    current_chars = unique_characters[page * 7:(page + 1) * 7]
    grouped = {k: list(v) for k, v in groupby(current_chars, key=lambda x: x['anime'])}

    for anime, group_chars in grouped.items():
        anime_total = await collection.count_documents({'anime': anime})
        harem_msg += f"\n⥱ {anime} ({len(group_chars)}/{anime_total})\n"
        for c in group_chars:
            count = character_counts.get(c['id'], 1)
            harem_msg += f"➥ {c['id']} | {c['rarity']} | {c['name']} ×{count}\n"

    total_count = len(user['characters'])
    keyboard = [[
        InlineKeyboardButton(f"📁 See Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}")
    ]]

    if total_pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️", callback_data=f"harem:{page - 1}:{user_id}"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("➡️", callback_data=f"harem:{page + 1}:{user_id}"))
        keyboard.append(nav)

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Select image (favorite or random)
    image_url = None
    if user.get('favorites'):
        fav_id = user['favorites'][0]
        fav_char = next((c for c in user['characters'] if c['id'] == fav_id), None)
        image_url = fav_char.get("img_url") if fav_char else None
    if not image_url:
        rand_char = random.choice(user['characters'])
        image_url = rand_char.get("img_url")

    if isinstance(event, Message):
        if image_url:
            await event.reply_photo(photo=image_url, caption=harem_msg, reply_markup=reply_markup)
        else:
            await event.reply(harem_msg, reply_markup=reply_markup)
    elif isinstance(event, CallbackQuery):
        try:
            if image_url:
                media = InputMediaPhoto(media=image_url, caption=harem_msg)
                await event.edit_message_media(media=media, reply_markup=reply_markup)
            else:
                await event.edit_message_caption(caption=harem_msg, reply_markup=reply_markup)
        except Exception:
            await event.edit_message_text(harem_msg, reply_markup=reply_markup)