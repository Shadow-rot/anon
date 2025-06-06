import os
import textwrap
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app

from moviepy.editor import VideoFileClip
import tempfile
import cairosvg

FONT_PATH = "./AnonXMusic/assets/default.ttf"


@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to an image, sticker, or video sticker.")

    if len(message.text.split()) < 2:
        return await message.reply_text("Send text after /mmf. Use `;` to separate top and bottom text.")

    reply = message.reply_to_message
    text = message.text.split(None, 1)[1]

    msg = await message.reply("Processing...")

    try:
        media = BytesIO()
        await reply.download(media)
        media.seek(0)

        # Handle sticker formats
        if reply.sticker:
            if reply.sticker.is_animated:  # .tgs (Lottie)
                webp_path = await convert_tgs_to_webp(media)
            elif reply.sticker.is_video:  # .mp4
                webp_path = await convert_mp4_sticker_to_webp(media)
            else:  # .webp static sticker
                webp_path = await process_static_image(media, text)
        elif reply.photo or reply.document or reply.video:
            webp_path = await process_static_image(media, text)
        else:
            return await msg.edit("Unsupported media type.")
    except Exception as e:
        return await msg.edit(f"Failed to process media: `{e}`")

    await app.send_document(message.chat.id, webp_path)
    await msg.delete()
    os.remove(webp_path)


async def process_static_image(buffer, text):
    image = Image.open(buffer).convert("RGB")
    return await draw_text_on_image(image, text)


async def draw_text_on_image(img, text):
    i_width, i_height = img.size
    font_size = int((70 / 640) * i_width)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw = ImageDraw.Draw(img)

    if ";" in text:
        upper_text, lower_text = text.split(";", 1)
    else:
        upper_text = text
        lower_text = ""

    current_h, pad = 10, 5
    for line in textwrap.wrap(upper_text, width=15):
        uwl, uht, uwr, uhb = font.getbbox(line)
        w, h = uwr - uwl, uhb - uht
        x = (i_width - w) / 2
        y = int((current_h / 640) * i_width)
        shadow_text(draw, line, x, y, font)
        current_h += h + pad

    if lower_text:
        for line in textwrap.wrap(lower_text, width=15):
            uwl, uht, uwr, uhb = font.getbbox(line)
            w, h = uwr - uwl, uhb - uht
            x = (i_width - w) / 2
            y = i_height - h - int((20 / 640) * i_width)
            shadow_text(draw, line, x, y, font)

    out_path = f"meme_{os.getpid()}.webp"
    img.save(out_path, "webp")
    return out_path


def shadow_text(draw, text, x, y, font):
    # Black shadow
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((x + dx, y + dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")


async def convert_tgs_to_webp(tgs_buffer: BytesIO):
    """Convert .tgs (Lottie) to PNG, then add text and convert to WEBP."""
    png_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    webp_path = f"meme_{os.getpid()}.webp"

    try:
        cairosvg.svg2png(bytestring=tgs_buffer.read(), write_to=png_path)
        img = Image.open(png_path)
        os.remove(png_path)
        return await draw_text_on_image(img, "TGS Sticker")
    except Exception as e:
        raise RuntimeError(f"TGS conversion failed: {e}")


async def convert_mp4_sticker_to_webp(video_buffer: BytesIO):
    """Convert .mp4 sticker to first frame PNG, then to WEBP with meme text."""
    video_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    with open(video_path, "wb") as f:
        f.write(video_buffer.read())

    clip = VideoFileClip(video_path)
    frame_path = f"{video_path}.jpg"
    clip.save_frame(frame_path, t=0.0)
    clip.reader.close()
    clip.close()
    os.remove(video_path)

    img = Image.open(frame_path)
    os.remove(frame_path)
    return await draw_text_on_image(img, "MP4 Sticker")