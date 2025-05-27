import re
import aiohttp
import aiofiles
import os
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app
from config import LOGGER_ID

INSTAGRAM_REGEX = r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/reel/.*$"
COMMANDS = ["ig", "instagram", "reel"]

@app.on_message(filters.command(COMMANDS) | filters.regex(INSTAGRAM_REGEX))
async def download_instagram_video(client, message: Message):
    if message.command and len(message.command) < 2:
        return await message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL.")
    
    url = message.text.split()[1] if message.command else message.text.strip()

    if not re.match(INSTAGRAM_REGEX, url):
        return await message.reply_text("❌ This is not a valid Instagram reel link.")

    a = await message.reply_text("⏳ Processing...")

    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                result = await resp.json()
                if result.get("error"):
                    raise Exception("API error or unsupported reel.")
                video_url = result["result"]["url"]
    except Exception as e:
        await a.edit(f"❌ Failed to fetch video info:\n{e}")
        await app.send_message(LOGGER_ID, f"Instagram fetch error:\n{e}")
        return

    temp_path = "reel.mp4"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, headers=headers) as video_resp:
                if video_resp.status != 200:
                    raise Exception(f"Download failed with status code {video_resp.status}")
                async with aiofiles.open(temp_path, mode='wb') as f:
                    await f.write(await video_resp.read())

        await a.delete()
        await message.reply_video(video=temp_path, caption="Powered by: @lovely_xu_bot")

    except Exception as e:
        await message.reply_text(f"❌ Failed to upload video:\n{e}")
        await app.send_message(LOGGER_ID, f"Upload error:\n{e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)