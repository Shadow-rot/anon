import re
import httpx
from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic import app

API_URL = "https://www.alphaapis.org/Instagram/dl/v1"

# Regex pattern to match Instagram URLs
INSTAGRAM_URL_PATTERN = r"(https?://(?:www\.)?instagram\.com/[^\s]+)"

@app.on_message(filters.command(["ig", "insta"]) | filters.regex(INSTAGRAM_URL_PATTERN))
async def insta_download(client: Client, message: Message):
    matched_url = None

    if message.command and len(message.command) > 1:
        instagram_url = message.command[1]
    else:
        urls = re.findall(INSTAGRAM_URL_PATTERN, message.text)
        if urls:
            instagram_url = urls[0]
        else:
            return await message.reply_text("❌ Please provide a valid Instagram URL.")

    processing_message = await message.reply_text("🔄 Processing...")

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            response = await http.get(API_URL, params={"url": instagram_url})
            response.raise_for_status()
            data = response.json()

        results = data.get("result", [])

        if not results:
            return await processing_message.edit("⚠️ No media found. Please check the link.")

        for item in results:
            download_link = item.get("downloadLink")

            if not download_link:
                continue

            if ".mp4" in download_link:
                await message.reply_video(download_link)
            elif any(ext in download_link for ext in (".jpg", ".jpeg", ".png", ".webp")):
                await message.reply_photo(download_link)
            else:
                await message.reply_text(f"❌ Unsupported media type: {download_link}")

    except Exception as e:
        await processing_message.edit(f"❌ Error: {e}")
    finally:
        await processing_message.delete()