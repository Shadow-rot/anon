import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app

FONT_PATH = "./AnonXMusic/assets/default.ttf"
FONT_CACHE = ImageFont.truetype(FONT_PATH, 40)

@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text("Reply to an image or static sticker.")

    if len(message.text.split()) < 2:
        return await message.reply_text("Send text after /mmf like:\n`/mmf Hello;World`")

    msg = await message.reply_text("⚡ Processing...")
    text = message.text.split(None, 1)[1]
    
    # Download media
    media_path = await app.download_media(message.reply_to_message)
    
    # Create meme
    meme_path = await draw_text_fast(media_path, text)
    
    await message.reply_photo(photo=meme_path)
    await msg.delete()
    
    os.remove(meme_path)


async def draw_text_fast(image_path, text):
    img = Image.open(image_path).convert("RGB")
    os.remove(image_path)

    width, height = img.size
    draw = ImageDraw.Draw(img)
    font_size = int((40 / 640) * width)
    font = FONT_CACHE.font_variant(size=font_size)

    if ";" in text:
        top_text, bottom_text = text.split(";", 1)
    else:
        top_text, bottom_text = text, ""

    def draw_centered(text_lines, y_start):
        for line in textwrap.wrap(text_lines, width=20):
            w, h = draw.textsize(line, font=font)
            x = (width - w) / 2
            draw.text((x, y_start), line, font=font, fill="white")
            y_start += h + 5
        return y_start

    draw_centered(top_text, 10)
    if bottom_text:
        draw_centered(bottom_text, height - 60)

    out_path = "memified.jpg"  # Use JPG
    img.save(out_path, "JPEG")
    return out_path