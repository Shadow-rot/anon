import re
import requests
from pyrogram import filters
from AnonXMusic import app
from config import LOGGER_ID


# Regex to detect Instagram reel links
INSTAGRAM_REGEX = r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/reel/.*$"

# Supported commands
COMMANDS = ["ig", "instagram", "reel"]

@app.on_message(filters.command(COMMANDS) | filters.regex(INSTAGRAM_REGEX))
async def download_instagram_video(client, message):
    if message.command:
        if len(message.command) < 2:
            return await message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ URL.")
        url = message.text.split()[1]
    else:
        url = message.text.strip()

    # Validate URL
    if not re.match(INSTAGRAM_REGEX, url):
        return await message.reply_text(" ᴛʜɪs ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ʟɪɴᴋ.")

    a = await message.reply_text(" Processing...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    response = requests.get(api_url)
    try:
        result = response.json()
        data = result["result"]
    except Exception as e:
        f = f"❌ ᴇʀʀᴏʀ:\n{e}"
        try:
            await a.edit(f)
        except Exception:
            await message.reply_text(f)
        return await app.send_message(LOGGER_ID, f)

    if not result["error"]:
        video_url = data["url"]
        caption = (
            f" Powered by: @lovely_xu_bot"
        )

        await a.delete()
        await message.reply_video(video_url, caption=caption)
    else:
        try:
            return await a.edit("❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ.")
        except Exception:
            return await message.reply_text("❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ.")


__MODULE__ = "Rᴇᴇʟ"
__HELP__ = """
**Instagram Reel Downloader:**

• `/ig [URL]` - Download Instagram reels.
• `/instagram [URL]` - Download Instagram reels.
• `/reel [URL]` - Download Instagram reels.
• **Send an Instagram reel link directly** - The bot will automatically process it.
"""