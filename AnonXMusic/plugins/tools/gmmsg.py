import re
import random
from pyrogram import filters
from AnonXMusic import app
from AnonXMusic.utils.autofix import auto_fix_handler  # Import the AutoFix wrapper


# AutoFix-protected handler
@app.on_message(filters.command(["m", "goodmorning"], prefixes=["g", "G", "morning"]))
@auto_fix_handler
def goodmorning_command_handler(_, message):
    sender = message.from_user.mention
    send_video = random.choice([True, False])
    if send_video:
        video_url = get_random_video()
        app.send_video(message.chat.id, video_url)
        message.reply_text(f"Good Morning, {sender}! Wakeup fast. 🥰 Babe")
    else:
        emoji = get_random_emoji()
        app.send_message(message.chat.id, emoji)
        message.reply_text(f"Good Morning cutie, {sender}! Wakeup fast. {emoji}")


def get_random_video():
    return random.choice([
        "https://files.catbox.moe/aaf374.mp4",
        "https://files.catbox.moe/ydjas6.mp4",
        "https://files.catbox.moe/sm4i57.mp4",
        "https://telegra.ph/file/941f1237d433974398b12.mp4",
    ])


def get_random_emoji():
    return random.choice(["🥰", "🥱", "🤗"])