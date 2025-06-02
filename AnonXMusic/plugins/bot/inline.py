from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)
from youtubesearchpython.__future__ import VideosSearch

from AnonXMusic import app
from AnonXMusic.utils.inlinequery import answer  # Your default inline results
from config import BANNED_USERS


@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client: Client, query):
    text = query.query.strip().lower()
    answers = []

    if not text:
        try:
            await client.answer_inline_query(query.id, results=answer, cache_time=10)
        except Exception:
            return
        return

    # Search videos using YouTubeSearchPython
    try:
        search = VideosSearch(text, limit=20)
        result = (await search.next()).get("result", [])
    except Exception:
        return

    for video in result:
        title = video.get("title", "No Title").title()
        duration = video.get("duration", "N/A")
        views = video.get("viewCount", {}).get("short", "0 views")
        thumbnail = video.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
        channellink = video.get("channel", {}).get("link", "#")
        channel = video.get("channel", {}).get("name", "Unknown Channel")
        link = video.get("link", "#")
        published = video.get("publishedTime", "Unknown")

        description = f"{views} | {duration} ᴍɪɴᴜᴛᴇs | {channel} | {published}"
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="ʏᴏᴜᴛᴜʙᴇ 🎄", url=link)]]
        )

        searched_text = f"""
❄ <b>ᴛɪᴛʟᴇ :</b> <a href="{link}">{title}</a>

⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {duration} ᴍɪɴᴜᴛᴇs
👀 <b>ᴠɪᴇᴡs :</b> <code>{views}</code>
🎥 <b>ᴄʜᴀɴɴᴇʟ :</b> <a href="{channellink}">{channel}</a>
⏰ <b>ᴘᴜʙʟɪsʜᴇᴅ ᴏɴ :</b> {published}

<u><b>➻ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴍᴏᴅᴇ ʙʏ {app.name}</b></u>"""

        answers.append(
            InlineQueryResultPhoto(
                photo_url=thumbnail,
                title=title,
                thumb_url=thumbnail,
                description=description,
                caption=searched_text,
                reply_markup=buttons,
            )
        )

    if answers:
        try:
            await client.answer_inline_query(query.id, results=answers, cache_time=10)
        except Exception:
            return
    else:
        try:
            await client.answer_inline_query(
                query.id,
                results=answer,
                cache_time=10,
                switch_pm_text="No results found. Tap to start bot.",
                switch_pm_parameter="start",
            )
        except Exception:
            return