import os
import textwrap
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app

FONT_PATH = "./AnonXMusic/assets/default.ttf"  # fallback font

def get_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


@app.on_message(filters.command("mmf"))
async def mmf_handler(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to an image or video with `/mmf text`.", quote=True)

    if len(message.text.split()) < 2:
        return await message.reply("Provide some text after /mmf, like:\n`/mmf top;bottom`")

    text = message.text.split(None, 1)[1]
    reply = message.reply_to_message

    if not (reply.photo or reply.document or reply.video or reply.animation):
        return await message.reply("Reply to a **photo or short video (MP4)**.")

    temp_file = await app.download_media(reply, file_name="mmf_temp")
    msg = await message.reply("Processing...")

    try:
        image_path = await convert_to_image(temp_file)
        meme_file = await draw_text_on_image(image_path, text)
        await app.send_document(message.chat.id, document=meme_file)
    except Exception as e:
        await msg.edit(f"❌ Failed to memify:\n`{e}`")
        return
    finally:
        await msg.delete()
        for f in [temp_file, "frame.jpg", "memify.webp"]:
            if os.path.exists(f):
                os.remove(f)


async def convert_to_image(path: str) -> str:
    if path.endswith((".mp4", ".mkv", ".webm", ".mov")):
        output_frame = "frame.jpg"
        subprocess.run([
            "ffmpeg", "-i", path, "-vf", "scale=512:-1", "-vframes", "1", output_frame,
            "-y", "-loglevel", "quiet"
        ])
        return output_frame
    else:
        return path


async def draw_text_on_image(image_path: str, text: str) -> str:
    img = Image.open(image_path).convert("RGB")
    i_width, i_height = img.size

    font = get_font(int((70 / 640) * i_width))
    draw = ImageDraw.Draw(img)

    if ";" in text:
        upper_text, lower_text = text.split(";", 1)
    else:
        upper_text, lower_text = text, ""

    current_h, pad = 10, 5

    def draw_text_block(text, y_offset):
        for line in textwrap.wrap(text, width=15):
            bbox = font.getbbox(line)
            u_width, u_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (i_width - u_width) / 2
            y = y_offset

            # Black border
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                draw.text((x + dx, y + dy), line, font=font, fill="black")
            draw.text((x, y), line, font=font, fill="white")
            y_offset += u_height + pad
        return y_offset

    if upper_text:
        current_h = draw_text_block(upper_text, current_h)

    if lower_text:
        draw_text_block(lower_text, i_height - int((100 / 640) * i_width))

    output_path = "memify.webp"
    img.save(output_path, "webp")
    return output_path