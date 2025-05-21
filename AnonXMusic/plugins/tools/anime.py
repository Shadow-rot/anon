import os
import aiohttp
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from datetime import datetime
from pyrogram import filters
from AnonXMusic import app

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


@app.on_message(filters.command("anime"))
async def anime_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /anime <anime name>")

    data = await fetch_json(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("No anime found.")

    anime = data["data"][0]
    title = anime['title']
    score = anime.get('score', 'N/A')
    episodes = anime.get('episodes', 'N/A')
    status = anime.get('status', 'N/A')
    aired = anime.get('aired', {}).get('string', 'N/A')
    url = anime['url']
    image = anime['images']['jpg']['image_url']

    caption = (
        f"{title}*\n"
        f"Score: {score}\n"
        f"Episodes: {episodes}\n"
        f"Status: {status}\n"
        f"Aired: {aired}\n\n"
        f"_Message provided by [Siya](https://t.me/siyaprobot)_"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("View on MyAnimeList", url=url)]]
    )

    await message.reply_photo(
        photo=image,
        caption=caption,
        reply_markup=buttons,
        parse_mode="markdown"
    )


@app.on_message(filters.command("manga"))
async def manga_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /manga <manga name>")

    data = await fetch_json(f"https://api.jikan.moe/v4/manga?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("No manga found.")

    manga = data["data"][0]
    await message.reply(
        f"**{manga['title']}**\n"
        f"Score: {manga.get('score', 'N/A')}\n"
        f"Chapters: {manga.get('chapters', 'N/A')}\n"
        f"Status: {manga.get('status', 'N/A')}\n"
        f"URL: {manga['url']}"
    )


@app.on_message(filters.command("character"))
async def character_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /character <character name>")

    data = await fetch_json(f"https://api.jikan.moe/v4/characters?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("No character found.")

    char = data["data"][0]
    await message.reply(
        f"**{char['name']}**\n"
        f"About: {char.get('about', 'N/A')[:500]}...\n"
        f"URL: {char['url']}"
    )


@app.on_message(filters.command("user"))
async def user_info(_, message):
    username = " ".join(message.command[1:])
    if not username:
        return await message.reply("Usage: /user <MyAnimeList username>")

    data = await fetch_json(f"https://api.jikan.moe/v4/users/{username}")
    if not data or not data.get("data"):
        return await message.reply("User not found.")

    user = data["data"]
    stats = user.get("statistics", {})
    await message.reply(
        f"**{user['username']}**\n"
        f"Watching: {stats.get('anime', {}).get('watching', 'N/A')}\n"
        f"Completed: {stats.get('anime', {}).get('completed', 'N/A')}\n"
        f"Plan to Watch: {stats.get('anime', {}).get('plan_to_watch', 'N/A')}\n"
        f"URL: https://myanimelist.net/profile/{username}"
    )


@app.on_message(filters.command("upcoming"))
async def upcoming_anime(_, message):
    data = await fetch_json("https://api.jikan.moe/v4/seasons/upcoming?limit=10")
    if not data or not data.get("data"):
        return await message.reply("No upcoming anime found.")

    result = "\n".join([anime['title'] for anime in data["data"]])
    await message.reply(f"**Upcoming Anime:**\n{result}")


@app.on_message(filters.command("airing"))
async def airing_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /airing <anime name>")

    data = await fetch_json(f"https://api.jikan.moe/v4/anime?q={query}&limit=1")
    if not data or not data.get("data"):
        return await message.reply("Anime not found.")

    anime = data["data"][0]
    airing_status = anime.get("status", "N/A")
    broadcast = anime.get("broadcast", {}).get("string", "N/A")

    await message.reply(
        f"**{anime['title']}**\n"
        f"Status: {airing_status}\n"
        f"Broadcast Time: {broadcast}\n"
        f"URL: {anime['url']}"
    )


@app.on_message(filters.command("latest"))
async def latest_airing(_, message):
    day = datetime.utcnow().strftime("%A").lower()
    data = await fetch_json(f"https://api.jikan.moe/v4/schedules?filter={day}")
    if not data or not data.get("data"):
        return await message.reply("Couldn't get today's airing list.")

    titles = "\n".join([anime['title'] for anime in data["data"][:10]])
    await message.reply(f"**Animes Airing Today ({day.title()}):**\n{titles}")


async def scrape_site(base_url, query):
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + query.replace(" ", "+")) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            results = soup.find_all("h2")
            return "\n".join(r.text.strip() for r in results[:5]) or "No results found."


@app.on_message(filters.command("kaizoku"))
async def kaizoku(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /kaizoku <anime name>")
    result = await scrape_site("https://animekaizoku.com/?s=", query)
    await message.reply(f"**Kaizoku Results:**\n{result}")


@app.on_message(filters.command("kayo"))
async def kayo(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /kayo <anime name>")
    result = await scrape_site("https://animekayo.com/?s=", query)
    await message.reply(f"**Kayo Results:**\n{result}")


@app.on_message(filters.command("whatanime") & filters.reply)
async def whatanime(_, message):
    if not message.reply_to_message.photo and not message.reply_to_message.animation:
        return await message.reply("Reply to an image or gif.")
    
    file_path = await message.reply_to_message.download()
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            image_data = f.read()
        form = aiohttp.FormData()
        form.add_field("image", image_data, filename="anime.jpg", content_type="image/jpeg")
        async with session.post("https://api.trace.moe/search", data=form) as resp:
            result = await resp.json()

            if "result" not in result or not result["result"]:
                return await message.reply("No anime source found.")

            top = result["result"][0]
            await message.reply(
                f"**Anime Found:**\n"
                f"Title: {top['filename']}\n"
                f"Episode: {top['episode']}\n"
                f"Similarity: {round(top['similarity'] * 100, 2)}%\n"
                f"From {top['from']}s to {top['to']}s"
            )