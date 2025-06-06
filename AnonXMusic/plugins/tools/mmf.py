import os
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app

# Load font once globally
if os.name == "nt":
    FONT_PATH = "arial.ttf"
else:
    FONT_PATH = "./AnonXMusic/assets/default.ttf"

FONT_SIZE_RATIO = 70 / 640  # base font size ratio


@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    chat_id = message.chat.id
    reply_message = message.reply_to_message

    if not reply_message:
        return await message.reply_text("Reply to an image/sticker or mp4 sticker to memify.")

    if len(message.text.split()) < 2:
        return await message.reply_text("Give me text after /mmf to memify.")

    status_msg = await message.reply_text("Processing your meme... 🪐")
    text = message.text.split(None, 1)[1]

    # Download media as bytes
    media_bytes = await app.download_media(reply_message, file_name=BytesIO())
    if not media_bytes:
        await status_msg.edit("Failed to download media.")
        return

    try:
        memed_bytes = await draw_text_in_memory(media_bytes, text)
    except Exception as e:
        await status_msg.edit(f"Error processing media: {e}")
        return

    memed_bytes.seek(0)
    await app.send_document(chat_id, document=memed_bytes, filename="memify.webp")
    await status_msg.delete()


async def draw_text_in_memory(image_bytes: BytesIO, text: str) -> BytesIO:
    image_bytes.seek(0)
    img = Image.open(image_bytes).convert("RGBA")

    # Resize large images to max width 640px to speed up
    max_width = 640
    if img.width > max_width:
        w_percent = max_width / float(img.width)
        h_size = int(float(img.height) * w_percent)
        img = img.resize((max_width, h_size), Image.LANCZOS)

    font_size = int(img.width * FONT_SIZE_RATIO)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw = ImageDraw.Draw(img)

    # Split text for upper and lower parts
    if ";" in text:
        upper_text, lower_text = text.split(";", 1)
    else:
        upper_text, lower_text = text, ""

    def draw_text_with_outline(draw_obj, pos, text_str):
        x, y = pos
        # Draw outline (4 directions)
        outline_color = (0, 0, 0)
        draw_obj.text((x-1, y), text_str, font=font, fill=outline_color)
        draw_obj.text((x+1, y), text_str, font=font, fill=outline_color)
        draw_obj.text((x, y-1), text_str, font=font, fill=outline_color)
        draw_obj.text((x, y+1), text_str, font=font, fill=outline_color)
        # Draw main text
        draw_obj.text((x, y), text_str, font=font, fill=(255, 255, 255))

    y_offset = 10
    line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 5  # approximate height with padding

    # Draw upper text
    if upper_text.strip():
        for line in textwrap.wrap(upper_text.strip(), width=15):
            w, h = draw.textsize(line, font=font)
            x = (img.width - w) // 2
            draw_text_with_outline(draw, (x, y_offset), line)
            y_offset += line_height

    # Draw lower text
    if lower_text.strip():
        lines = textwrap.wrap(lower_text.strip(), width=15)
        y_offset = img.height - line_height * len(lines) - 10
        for line in lines:
            w, h = draw.textsize(line, font=font)
            x = (img.width - w) // 2
            draw_text_with_outline(draw, (x, y_offset), line)
            y_offset += line_height

    output_bytes = BytesIO()
    img.save(output_bytes, format="WEBP")
    output_bytes.name = "memify.webp"
    output_bytes.seek(0)
    return output_bytes