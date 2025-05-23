import asyncio
import aiohttp
from html import escape
from urllib.parse import quote_plus
from io import BytesIO
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from AnonXMusic import app

hindi_dub_cache = {}

# Reuse one aiohttp session
session = aiohttp.ClientSession()

async def fetch_json(url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.json()
        return None

async def fetch_image_bytes(url):
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.read()
        return None

async def check_hindi_dub(anime_title):
    if anime_title in hindi_dub_cache:
        return hindi_dub_cache[anime_title]
    try:
        search_url = f"https://animekaizoku.com/?s={quote_plus(anime_title)}"
        async with session.get(search_url) as resp:
            if resp.status != 200:
                return False
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            if "Hindi" in soup.get_text():
                hindi_dub_cache[anime_title] = True
                return True
    except Exception:
        pass
    hindi_dub_cache[anime_title] = False
    return False

async def send_anime_card(message, title, info, image_url, site_url, buttons=None):
    image_data = await fetch_image_bytes(image_url)
    if not image_data:
        return await message.reply("Failed to fetch image.")
    image_file = BytesIO(image_data)
    image_file.name = "anime.jpg"
    image_file.seek(0)

    caption = (
        f"<b>{escape(title)}</b>\n"
        f"{info}\n\n"
        f"<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
    )
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    return await message.reply_photo(photo=image_file, caption=caption, reply_markup=reply_markup)

@app.on_message(filters.command("anime"))
async def anime_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /anime <anime name>")

    fields = "title,score,episodes,status,images,type,duration,aired,rating,url"
    url = f"https://api.jikan.moe/v4/anime?q={quote_plus(query)}&limit=1&fields={fields}"
    data = await fetch_json(url)
    if not data or not data.get("data"):
        return await message.reply("No anime found.")
    
    anime = data["data"][0]
    info = (
        f"<b>Type:</b> {anime.get('type', 'N/A')} | "
        f"<b>Duration:</b> {anime.get('duration', 'N/A')}\n"
        f"<b>Episodes:</b> {anime.get('episodes', 'N/A')} | "
        f"<b>Status:</b> {anime.get('status', 'N/A')}\n"
        f"<b>Aired:</b> {anime.get('aired', {}).get('string', 'N/A')}\n"
        f"<b>Rating:</b> {anime.get('rating', 'N/A')} | "
        f"<b>Score:</b> {anime.get('score', 'N/A')}\n"
        f"<b>Hindi Dub:</b> <i>Checking...</i>"
    )

    buttons = [
        [InlineKeyboardButton("View on MyAnimeList", url=anime["url"])],
        [InlineKeyboardButton("Search on Kaizoku", url=f"https://animekaizoku.com/?s={quote_plus(query)}")],
        [InlineKeyboardButton("Search on Kayo", url=f"https://animekayo.com/?s={quote_plus(query)}")]
    ]

    reply = await send_anime_card(
        message, anime["title"], info,
        anime["images"]["jpg"]["large_image_url"],
        anime["url"], buttons
    )

    async def update_dub():
        dub = await check_hindi_dub(anime["title"])
        updated_info = info.replace("<i>Checking...</i>", "Available" if dub else "Not available")
        updated_caption = (
            f"<b>{escape(anime['title'])}</b>\n"
            f"{updated_info}\n\n"
            f"<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
        )
        try:
            await reply.edit_caption(updated_caption, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            pass

    asyncio.create_task(update_dub())

@app.on_message(filters.command("character"))
async def character_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /character <character name>")
    data = await fetch_json(f"https://api.jikan.moe/v4/characters?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("No character found.")
    char = data["data"][0]
    info = f"<b>About:</b> {char.get('about', 'No info available')[:500]}..."
    await send_anime_card(message, char['name'], info, char['images']['jpg']['image_url'], char['url'])


@app.on_message(filters.command("manga"))
async def manga_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /manga <manga name>")
    data = await fetch_json(f"https://api.jikan.moe/v4/manga?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("No manga found.")
    manga = data["data"][0]
    info = (
        f"<b>Score:</b> {manga.get('score', 'N/A')}\n"
        f"<b>Chapters:</b> {manga.get('chapters', 'N/A')}\n"
        f"<b>Status:</b> {manga.get('status', 'N/A')}\n"
        f"<b>Published:</b> {manga.get('published', {}).get('string', 'N/A')}"
    )
    await send_anime_card(message, manga['title'], info, manga['images']['jpg']['large_image_url'], manga['url'])


@app.on_message(filters.command("airing"))
async def airing_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /airing <anime name>")
    data = await fetch_json(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("No anime found.")
    anime = data["data"][0]
    info = (
        f"<b>Status:</b> {anime.get('status', 'N/A')}\n"
        f"<b>Episodes:</b> {anime.get('episodes', 'N/A')}\n"
        f"<b>Aired:</b> {anime.get('aired', {}).get('string', 'N/A')}"
    )
    await send_anime_card(message, anime['title'], info, anime['images']['jpg']['large_image_url'], anime['url'])


@app.on_message(filters.command("upcoming"))
async def upcoming_anime(_, message):
    data = await fetch_json("https://api.jikan.moe/v4/seasons/upcoming")
    if not data or not data.get("data"):
        return await message.reply("No upcoming anime found.")
    text = "<b>Upcoming Anime:</b>\n\n"
    for anime in data["data"][:10]:
        text += f"<a href='{anime['url']}'>{anime['title']}</a>\n"
    text += "\n<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
    await message.reply(text, disable_web_page_preview=True)


@app.on_message(filters.command("latest"))
async def latest_anime(_, message):
    data = await fetch_json("https://api.jikan.moe/v4/seasons/now")
    if not data or not data.get("data"):
        return await message.reply("No airing anime found.")
    text = "<b>Currently Airing:</b>\n\n"
    for anime in data["data"][:10]:
        text += f"<a href='{anime['url']}'>{anime['title']}</a>\n"
    text += "\n<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
    await message.reply(text, disable_web_page_preview=True)


@app.on_message(filters.command("user"))
async def user_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /user <username>")
    data = await fetch_json(f"https://api.jikan.moe/v4/users/{query}")
    if not data or not data.get("data"):
        return await message.reply("User not found.")
    user = data["data"]
    info = (
        f"<b>Username:</b> {user['username']}\n"
        f"<b>Gender:</b> {user.get('gender', 'N/A')}\n"
        f"<b>Joined:</b> {user.get('joined', 'N/A')}"
    )
    await send_anime_card(message, user['username'], info, user['images']['jpg']['image_url'], user['url'])


@app.on_message(filters.command("kaizoku"))
async def search_kaizoku(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /kaizoku <anime>")
    search_url = f"https://animekaizoku.com/?s={query.replace(' ', '+')}"
    reply = f"<b>Results for:</b> {query}\n<a href='{search_url}'>View on AnimeKaizoku</a>\n\n<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
    await message.reply(reply, disable_web_page_preview=True)


@app.on_message(filters.command("kayo"))
async def search_kayo(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /kayo <anime>")
    search_url = f"https://animekayo.com/?s={query.replace(' ', '+')}"
    reply = f"<b>Results for:</b> {query}\n<a href='{search_url}'>View on AnimeKayo</a>\n\n<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
    await message.reply(reply, disable_web_page_preview=True)


@app.on_message(filters.command("whatanime"))
async def what_anime(_, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("Reply to an anime image or gif.")
    file_path = await message.reply_to_message.download()
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            async with session.post("https://api.trace.moe/search", data={"image": f.read()}) as resp:
                result = await resp.json()
    if not result.get("result"):
        return await message.reply("No result found.")
    top = result["result"][0]
    text = (
        f"<b>Anime:</b> {top['anime']}\n"
        f"<b>Episode:</b> {top['episode']}\n"
        f"<b>At:</b> {top['from']}s to {top['to']}s\n"
        f"<b>Similarity:</b> {round(top['similarity'] * 100, 2)}%\n\n"
        f"<i>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></i>"
    )
    await message.reply(text)