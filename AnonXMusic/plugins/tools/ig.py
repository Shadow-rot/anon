import re
import httpx
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

DOWNLOADING_STICKER_ID = "CAACAgEAAx0CfD7LAgACO7xmZzb83lrLUVhxtmUaanKe0_ionAAC-gADUSkNORIJSVEUKRrhHgQ"
INSTAGRAM_REGEX = r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/(reel|p|tv)/[^\s/?]+"
ALT_API_URL = "https://insta-dl.hazex.workers.dev/?url="

@app.on_message(filters.command(["ig", "insta"]) | filters.regex(INSTAGRAM_REGEX))
async def download_instagram_reel(client, message):
    url = None

    # Get URL from command or plain text
    if message.command and len(message.command) > 1:
        url = message.command[1]
    else:
        match = re.search(INSTAGRAM_REGEX, message.text)
        if match:
            url = match.group(0)

    if not url:
        return await message.reply_text("❌ Please provide a valid Instagram reel or post URL.")

    sticker = await message.reply_sticker(DOWNLOADING_STICKER_ID)

    try:
        async with httpx.AsyncClient() as session:
            response = await session.get(ALT_API_URL + url)
            response.raise_for_status()
            data = await response.json()

        video_url = (
            data.get("media") or
            data.get("video_url") or
            data.get("result", {}).get("url")
        )

        if not video_url or not video_url.startswith("http"):
            return await message.reply_text("❌ Could not extract video. It may be private or broken.")

        bot = await app.get_me()
        caption = f"[{bot.first_name}](https://t.me/{bot.username}) powered this."

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Open on Instagram", url=url)]]
        )

        if video_url.endswith((".jpg", ".jpeg", ".png")):
            await message.reply_photo(video_url, caption=caption, parse_mode="markdown", reply_markup=buttons)
        else:
            await message.reply_video(video_url, caption=caption, parse_mode="markdown", reply_markup=buttons)

    except httpx.HTTPStatusError as e:
        await message.reply_text(f"❌ Scraper error:\n`{e.response.text}`")
    except Exception as e:
        await message.reply_text(f"❌ Unexpected error:\n`{str(e)}`")
    finally:
        await sticker.delete()