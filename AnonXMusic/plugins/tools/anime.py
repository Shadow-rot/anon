import aiohttp
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

API = "https://api.jikan.moe/v4/anime"

# Hindi dub checker (AnimeKaizoku / AnimeVerse)
async def check_hindi_dub(title: str):
    search_sites = [
        "https://animekaizoku.com",
        "https://animeverse.in"
    ]
    async with aiohttp.ClientSession() as session:
        for site in search_sites:
            async with session.get(f"{site}/?s={title.replace(' ', '+')}") as res:
                text = await res.text()
                if title.lower() in text.lower():
                    return site
    return None

@app.on_message(filters.command("anime"))
async def anime_info(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("🔍 Please provide an anime name.")

    query = message.text.split(maxsplit=1)[1]
    msg = await message.reply("🔎 Fetching anime details...")

    try:
        async with aiohttp.ClientSession() as session:
            # Basic anime info
            async with session.get(f"{API}?q={query}&limit=1") as resp:
                data = await resp.json()
            if not data["data"]:
                return await msg.edit("❌ No results found.")
            anime = data["data"][0]

            # Full details
            async with session.get(f"{API}/{anime['mal_id']}/full") as full_resp:
                full_data = await full_resp.json()
                full = full_data.get("data", anime)

            # Relations for sequel
            async with session.get(f"{API}/{anime['mal_id']}/relations") as relr:
                rel_data = await relr.json()
                sequel = None
                for rel in rel_data.get("data", []):
                    if rel["relation"] == "Sequel":
                        sequel = rel["entry"][0]
                        break

        # Hindi dub check (background)
        hindi_dub = await check_hindi_dub(anime.get("title", ""))

        # Extract fields
        title = anime.get("title", "N/A")
        en_title = anime.get("title_english", "N/A")
        jp_title = anime.get("title_japanese", "N/A")
        mal_id = anime.get("mal_id")
        image = anime.get("images", {}).get("jpg", {}).get("large_image_url", "")
        url = anime.get("url", "")
        score = anime.get("score", "N/A")
        duration = anime.get("duration", "N/A")
        source = anime.get("source", "N/A")
        status = anime.get("status", "N/A")
        episodes = anime.get("episodes", "N/A")
        genres = ", ".join([g["name"] for g in anime.get("genres", [])]) or "N/A"
        tags = ", ".join([t["name"] for t in anime.get("themes", [])]) or "N/A"
        anime_type = anime.get("type", "N/A")
        rating = anime.get("rating", "N/A")
        aired = anime.get("aired", {}).get("string", "Unknown")
        trailer = anime.get("trailer", {}).get("url")

        # Format caption
        caption = f"""
<b>⥤ 𝙏𝙞𝙩𝙡𝙚 :</b> <code>{title}</code>
<b>⥤ 𝙀𝙣𝙜𝙡𝙞𝙨𝙝 :</b> {en_title}
<b>⥤ 𝙅𝙖𝙥𝙖𝙣𝙚𝙨𝙚 :</b> {jp_title}

<b>🆔 MAL ID:</b> <code>{mal_id}</code>
<b>🎬 Type:</b> {anime_type} | <b>📚 Source:</b> {source}
<b>📊 Score:</b> {score} | <b>🎞 Rating:</b> {rating}
<b>⏱ Duration:</b> {duration}
<b>📌 Status:</b> {status} | <b>📺 Episodes:</b> {episodes}
<b>🗓 Aired:</b> {aired}

<b>🎭 Genres:</b> <i>{genres}</i>
<b>🏷 Tags:</b> <i>{tags}</i>
<b>🔈 Hindi Dub:</b> {"✅ Found at " + hindi_dub if hindi_dub else "❌ Not found"}

<i>📡 Powered by <a href='https://t.me/siyaprobot'>Siya</a></i>
"""

        # Inline buttons
        buttons = [[InlineKeyboardButton("🌐 MAL Page", url=url)]]
        if trailer:
            buttons[0].append(InlineKeyboardButton("🎞 Trailer", url=trailer))
        if full.get("synopsis"):
            buttons.append([InlineKeyboardButton("📖 Synopsis", url=url + "#synopsis")])
        if sequel:
            buttons.append([InlineKeyboardButton(f"➡️ Sequel: {sequel['name']}", url=sequel["url"])])

        await msg.delete()
        await message.reply_photo(
            photo=image,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        await message.reply(f"⚠️ Error:\n<code>{e}</code>", parse_mode=ParseMode.HTML)