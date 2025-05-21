import os
import aiohttp
from bs4 import BeautifulSoup
from jikanpy import AioJikan
from pyrogram import filters
from AnonXMusic import app

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.on_message(filters.command("anime"))
async def anime_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /anime <anime name>")
    
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await message.reply("Failed to fetch anime info.")
            data = await resp.json()
    
    if not data.get("data"):
        return await message.reply("No anime found.")
    
    anime = data["data"][0]
    await message.reply(
        f"**{anime['title']}**\n"
        f"Score: {anime.get('score', 'N/A')}\n"
        f"Episodes: {anime.get('episodes', 'N/A')}\n"
        f"Status: {anime.get('status', 'N/A')}\n"
        f"Aired: {anime.get('aired', {}).get('string', 'N/A')}\n"
        f"URL: {anime['url']}"
    )
@app.on_message(filters.command("manga"))
async def manga_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /manga <manga name>")
    async with AioJikan() as jikan:
        try:
            result = await jikan.search("manga", query)
            manga = result["results"][0]
            await message.reply(
                f"**{manga['title']}**\n"
                f"Chapters: {manga['chapters']}\n"
                f"Score: {manga['score']}\n"
                f"URL: {manga['url']}"
            )
        except Exception as e:
            await message.reply(f"Error: {e}")

@app.on_message(filters.command("user"))
async def user_info(_, message):
    username = " ".join(message.command[1:])
    if not username:
        return await message.reply("Usage: /user <MAL username>")
    async with AioJikan() as jikan:
        try:
            user = await jikan.user(username)
            await message.reply(
                f"**{user['username']}**\n"
                f"Watching: {user['anime_stats']['watching']}\n"
                f"Completed: {user['anime_stats']['completed']}\n"
                f"URL: https://myanimelist.net/profile/{username}"
            )
        except Exception as e:
            await message.reply(f"Error: {e}")

@app.on_message(filters.command("upcoming"))
async def upcoming_anime(_, message):
    async with AioJikan() as jikan:
        try:
            season = await jikan.season_later()
            titles = [f"{anime['title']}" for anime in season["anime"][:10]]
            await message.reply("Upcoming Anime:\n" + "\n".join(titles))
        except Exception as e:
            await message.reply(f"Error: {e}")

@app.on_message(filters.command("airing"))
async def airing_info(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /airing <anime name>")
    async with AioJikan() as jikan:
        try:
            result = await jikan.search("anime", query)
            anime_id = result["results"][0]["mal_id"]
            anime = await jikan.anime(anime_id)
            await message.reply(
                f"**{anime['title']}**\n"
                f"Airing: {anime['airing']}\n"
                f"Aired: {anime['aired']['string']}\n"
                f"Next episode: {anime.get('broadcast', {}).get('time', 'N/A')}"
            )
        except Exception as e:
            await message.reply(f"Error: {e}")

async def scrape_site(url, query):
    async with aiohttp.ClientSession() as session:
        async with session.get(url + query.replace(" ", "+")) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            titles = soup.find_all("h2")
            return "\n".join(title.text.strip() for title in titles[:5]) or "No results found."

@app.on_message(filters.command("kaizoku"))
async def kaizoku(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /kaizoku <anime name>")
    results = await scrape_site("https://animekaizoku.com/?s=", query)
    await message.reply(f"Results for {query}:\n{results}")

@app.on_message(filters.command("kayo"))
async def kayo(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Usage: /kayo <anime name>")
    results = await scrape_site("https://animekayo.com/?s=", query)
    await message.reply(f"Results for {query}:\n{results}")

@app.on_message(filters.command("latest"))
async def latest_airing(_, message):
    async with AioJikan() as jikan:
        try:
            schedule = await jikan.schedule()
            from datetime import datetime
            today = datetime.utcnow().strftime('%A').lower()
            shows = schedule.get(today, [])
            titles = [a["title"] for a in shows[:10]]
            await message.reply("Animes airing today:\n" + "\n".join(titles))
        except Exception as e:
            await message.reply(f"Error: {e}")

@app.on_message(filters.command("whatanime") & filters.reply)
async def whatanime(_, message):
    if not message.reply_to_message.photo and not message.reply_to_message.animation:
        return await message.reply("Reply to an image or GIF.")
    file_path = await message.reply_to_message.download()
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            img_bytes = f.read()
        data = aiohttp.FormData()
        data.add_field("image", img_bytes)
        async with session.post("https://api.trace.moe/search", data=data) as resp:
            result = await resp.json()
            if "result" in result:
                top = result["result"][0]
                await message.reply(
                    f"**{top['filename']}**\n"
                    f"Episode: {top['episode']}\n"
                    f"Similarity: {round(top['similarity'] * 100, 2)}%\n"
                    f"From: {top['from']}s to {top['to']}s"
                )
            else:
                await message.reply("No result found.")