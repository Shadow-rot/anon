from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from AnonXMusic import app
from duckduckgo_search import DDGS
import re

@app.on_message(filters.command(["pic", "photo", "img"], prefixes=["/", "!", "."]))
async def duckduckgo_img_search(client: Client, message: Message):
    try:
        query = message.text.split(None, 1)[1]
    except IndexError:
        return await message.reply("⚠️ Please provide a search query.")

    # Extract optional limit
    lim_match = re.findall(r"lim=\d+", query)
    lim = int(lim_match[0].replace("lim=", "")) if lim_match else 5
    if lim_match:
        query = query.replace(f"lim={lim}", "").strip()

    msg = await message.reply("🔍 Searching images...")

    urls = []
    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, safesearch="moderate", max_results=lim * 2)
            for r in results:
                if r.get("image"):
                    urls.append(r["image"])
                if len(urls) >= lim:
                    break
    except Exception as e:
        return await msg.edit(f"❌ DuckDuckGo error:\n<code>{e}</code>\n\nTry again later or use /see for Unsplash search.")

    if not urls:
        return await msg.edit("❌ No results found.")

    try:
        await client.send_media_group(
            chat_id=message.chat.id,
            media=[InputMediaPhoto(media=url) for url in urls],
            reply_to_message_id=message.id
        )
        await msg.delete()
    except Exception as e:
        await msg.edit(f"⚠️ Failed to send images:\n<code>{e}</code>")