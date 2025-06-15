# plugins/song_downloader.py
import os
import re
import asyncio
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app
from AnonXMusic.misc import SUDOERS

# Configuration for yt-dlp with cookie support
def get_ytdl_opts():
    base_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    # Add cookies if available
    cookie_path = "cookies.txt"
    if os.path.exists(cookie_path):
        base_opts['cookiefile'] = cookie_path
        print("✅ Using cookies for YouTube authentication")
    else:
        print("⚠️ cookies.txt not found. Continuing without authentication")
        
    return base_opts

@app.on_message(filters.command("song", prefixes="/") & ~filters.bot)
async def song_downloader(_, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("Please provide a song name after /song")

    m = await message.reply_text("🔍 Searching...")
    
    try:
        # Search YouTube with custom options
        YTDL_OPTS = get_ytdl_opts()
        
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            info = await asyncio.to_thread(
                ydl.extract_info, 
                f"ytsearch:{query}", 
                download=False
            )
            
            if not info or 'entries' not in info or not info['entries']:
                return await m.edit("❌ No results found")
            
            video = info['entries'][0]
            title = video['title']
            url = video['webpage_url']
            duration = video.get('duration', 0)
            thumbnail = video.get('thumbnail')
            
        # Download button
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎵 Download MP3", callback_data=f"dl_{url}")]]
        )
        
        # Format duration
        minutes, seconds = divmod(duration, 60)
        duration_str = f"{minutes}:{seconds:02d}" if duration else "N/A"
        
        caption = f"**{title}**\n⏱️ Duration: `{duration_str}`"
        await m.delete()
        
        if thumbnail:
            await message.reply_photo(
                thumbnail,
                caption=caption,
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                caption,
                reply_markup=keyboard
            )
            
    except yt_dlp.utils.DownloadError as e:
        if "Sign in to confirm" in str(e):
            await m.edit("⚠️ YouTube requires authentication. Add valid cookies.txt file!")
        else:
            await m.edit(f"⚠️ Download error: {str(e)}")
    except Exception as e:
        await m.edit(f"❌ Unexpected error: {str(e)}")

# Callback handler for download button
@app.on_callback_query(filters.regex(r"^dl_"))
async def download_callback(_, query):
    url = query.data.split("_", 1)[1]
    m = await query.message.reply_text("⬇️ Downloading...")
    
    try:
        # Sanitize filename
        def sanitize_filename(filename):
            return re.sub(r'[^\w\-_. ]', '', filename)
        
        # Download audio with custom options
        YTDL_OPTS = get_ytdl_opts()
        
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_file = os.path.splitext(filename)[0] + '.mp3'
            title = sanitize_filename(info.get('title', 'audio'))
            performer = sanitize_filename(info.get('uploader', 'Unknown Artist'))
        
        # Send audio file
        await query.message.reply_audio(
            mp3_file,
            title=title[:64],
            performer=performer[:64],
            thumb=info.get('thumbnail')
        )
        await m.delete()
        
    except yt_dlp.utils.DownloadError as e:
        if "Sign in to confirm" in str(e):
            await m.edit("⚠️ YouTube requires authentication. Add valid cookies.txt file!")
        else:
            await m.edit(f"⚠️ Download failed: {str(e)}")
    except Exception as e:
        await m.edit(f"❌ Unexpected error: {str(e)}")
    finally:
        # Cleanup
        if 'mp3_file' in locals() and os.path.exists(mp3_file):
            os.remove(mp3_file)

# Create downloads directory if not exists
os.makedirs("downloads", exist_ok=True)