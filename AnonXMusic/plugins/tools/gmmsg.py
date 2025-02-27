import re
from pyrogram import filters
import random
from AnonXMusic import app


 
@app.on_message(filters.command(["m","goodmorning"], prefixes=["g","G","morning"]))
def goodnight_command_handler(_, message):
    sender = message.from_user.mention
    send_video = random.choice([True, False])
    if send_video:
        video_id = get_random_video()
        app.send_video(message.chat.id, video_id)
        message.reply_text(f"Good Morning, {sender}! Wakeup fast. 🥰 Babe")
    else:
        emoji = get_random_emoji()
        app.send_message(message.chat.id, emoji)
        message.reply_text(f"Good Morning cutie, {sender}! Wakeup fast. {emoji}")


def get_random_video():
    videos = [
        "https://files.catbox.moe/aaf374.mp4", # video 1
        "https://files.catbox.moe/ydjas6.mp4", # video 2
        "https://files.catbox.moe/sm4i57.mp4", # video 3
        "https://telegra.ph/file/941f1237d433974398b12.mp4",
    ]
    return random.choice(videos)


def get_random_emoji():
    emojis = [
        "🥰",
        "🥱",
        "🤗",
    ]
    return random.choice(emojis)