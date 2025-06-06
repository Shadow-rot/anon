import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app
import io

@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    chat_id = message.chat.id
    reply_message = message.reply_to_message

    if not reply_message:
        await message.reply_text("Please reply to an image, sticker, or mp4 sticker to memify.")
        return

    if len(message.text.split()) < 2:
        await message.reply_text("Give me text after /mmf to memify.")
        return

    msg = await message.reply_text("Processing your meme... 🪐")
    text = message.text.split(None, 1)[1]

    # Download media
    file_path = await app.download_media(reply_message)

    # Open image depending on type
    img = None
    try:
        # If it's an animated sticker or mp4 sticker, extract first frame as image
        if reply_message.sticker and reply_message.sticker.is_animated:
            # Animated webp sticker: extract first frame using PIL ImageSequence
            im = Image.open(file_path)
            img = next(iter(Image.ImageSequence.Iterator(im))).convert("RGBA")

        elif reply_message.sticker and reply_message.sticker.is_video:
            # mp4 sticker - use moviepy to extract first frame
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(file_path)
            frame = clip.get_frame(0)  # first frame (numpy array)
            img = Image.fromarray(frame).convert("RGBA")
            clip.close()

        else:
            # Static image or static sticker
            img = Image.open(file_path).convert("RGBA")

    except Exception as e:
        await msg.edit(f"Failed to process image/sticker: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return

    if os.path.exists(file_path):
        os.remove(file_path)

    # Now add text to img
    meme_image_path = await drawTextOnImage(img, text)

    await app.send_document(chat_id, document=meme_image_path)

    await msg.delete()

    os.remove(meme_image_path)


async def drawTextOnImage(img: Image.Image, text: str) -> str:
    i_width, i_height = img.size

    # Choose font path (modify as per your font location)
    if os.name == "nt":
        fnt = "arial.ttf"
    else:
        fnt = "./AnonXMusic/assets/default.ttf"

    m_font = ImageFont.truetype(fnt, int((70 / 640) * i_width))

    if ";" in text:
        upper_text, lower_text = text.split(";", 1)
    else:
        upper_text = text
        lower_text = ""

    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    def draw_text_lines(lines, y_start):
        nonlocal current_h
        for line in lines:
            uwl, uht, uwr, uhb = m_font.getbbox(line)
            u_width, u_height = uwr - uwl, uhb - uht

            x = (i_width - u_width) / 2
            y = y_start

            # black outline
            outline_range = [-2, 2]
            for ox in outline_range:
                for oy in outline_range:
                    draw.text((x + ox, y + oy), line, font=m_font, fill=(0, 0, 0))

            # white main text
            draw.text((x, y), line, font=m_font, fill=(255, 255, 255))

            y_start += u_height + pad
        current_h = y_start

    if upper_text:
        upper_lines = textwrap.wrap(upper_text, width=15)
        draw_text_lines(upper_lines, current_h)

    if lower_text:
        lower_lines = textwrap.wrap(lower_text, width=15)
        # Draw lower text near bottom
        line_height = m_font.getbbox("Ay")[3] - m_font.getbbox("Ay")[1]
        start_y = i_height - (line_height + pad) * len(lower_lines) - 10
        draw_text_lines(lower_lines, start_y)

    # Save final image
    output_path = "memified.webp"
    img.save(output_path, "WEBP")
    return output_path


__mod_name__ = "mmf"