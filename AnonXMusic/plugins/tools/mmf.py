import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app

FONT_PATH = "./AnonXMusic/assets/default.ttf"  # Make sure this font exists

@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    reply = message.reply_to_message

    if not reply or not (reply.photo or reply.document or reply.sticker):
        return await message.reply_text("Reply to a PNG, JPG, or static sticker.")

    if len(message.text.split()) < 2:
        return await message.reply_text("Give some text to memify. Example:\n`/mmf hello;world`")

    text = message.text.split(None, 1)[1]

    msg = await message.reply_text("Creating meme...")

    try:
        file_path = await app.download_media(reply)
        meme_path = await draw_text(file_path, text)
        await message.reply_document(meme_path)
    except Exception as e:
        await message.reply_text(f"Failed to create meme:\n`{e}`")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists("memified.webp"):
            os.remove("memified.webp")
        await msg.delete()

async def draw_text(image_path, text):
    img = Image.open(image_path).convert("RGB")
    i_width, i_height = img.size

    font_size = int((70 / 640) * i_width)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw = ImageDraw.Draw(img)

    if ";" in text:
        upper_text, lower_text = text.split(";", 1)
    else:
        upper_text, lower_text = text, ""

    current_h = 10
    pad = 5

    # Draw top text
    for line in textwrap.wrap(upper_text, width=20):
        w, h = draw.textsize(line, font=font)
        x = (i_width - w) / 2
        draw_text_with_outline(draw, x, current_h, line, font)
        current_h += h + pad

    # Draw bottom text
    if lower_text:
        for line in textwrap.wrap(lower_text, width=20):
            w, h = draw.textsize(line, font=font)
            x = (i_width - w) / 2
            y = i_height - h - 20
            draw_text_with_outline(draw, x, y, line, font)

    output_path = "memified.webp"
    img.save(output_path, "webp")
    return output_path

def draw_text_with_outline(draw, x, y, text, font):
    outline_color = "black"
    main_color = "white"
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=main_color)