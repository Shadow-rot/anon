# AnonXMusic/plugins/harem.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from itertools import groupby
from html import escape
import math
import random

from AnonXMusic import app
from AnonXMusic.utils.harem_db import harem_collection as collection, harem_users as user_collection

@app.on_message(filters.command("harem"))
async def harem_cmd(client, message, page: int = 0):
    user_id = message.from_user.id
    user = await user_collection.find_one({"id": user_id})

    if not user or not user.get("characters"):
        return await message.reply_text("𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙉𝙤𝙩 𝙂𝙧𝙖𝙗𝙗𝙚𝙙 𝘼𝙣𝙮 𝙒𝙖𝙞𝙛𝙪 𝙔𝙚𝙩...")

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    unique_characters = list({c['id']: c for c in characters}.values())

    total_pages = math.ceil(len(unique_characters) / 7)
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"<b>{escape(message.from_user.first_name)}'s Harem - Page {page + 1}/{total_pages}</b>\n"
    current_characters = unique_characters[page * 7:(page + 1) * 7]
    current_grouped = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, chars in current_grouped.items():
        total_in_anime = await collection.count_documents({"anime": anime})
        harem_message += f'\n⥱ <b>{anime} {len(chars)}/{total_in_anime}</b>\n'
        for char in chars:
            count = character_counts[char['id']]
            harem_message += f'➥{char["id"]}| {char["rarity"]} |{char["name"]} ×{count}\n'

    total_count = len(user['characters'])
    keyboard = [[
        InlineKeyboardButton(f"See Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}")
    ]]

    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"harem:{page - 1}:{user_id}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"harem:{page + 1}:{user_id}"))
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    img = None
    if 'favorites' in user and user['favorites']:
        fav_id = user['favorites'][0]
        char = next((c for c in user['characters'] if c['id'] == fav_id), None)
        img = char.get("img_url") if char else None
    elif user['characters']:
        img = random.choice(user['characters']).get("img_url")

    if img:
        await message.reply_photo(photo=img, caption=harem_message, reply_markup=reply_markup, parse_mode="html")
    else:
        await message.reply_text(harem_message, reply_markup=reply_markup, parse_mode="html")


@app.on_callback_query(filters.regex(r"^harem:(-?\d+):(\d+)$"))
async def harem_callback(client, callback_query):
    page, user_id = map(int, callback_query.data.split(":")[1:])
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("It's not your harem!", show_alert=True)

    message = callback_query.message
    message.from_user = callback_query.from_user
    await harem_cmd(client, message, page=page)