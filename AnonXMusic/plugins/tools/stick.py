from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw import functions, types
from uuid import uuid4
import os
from PIL import Image
import tempfile
from AnonXMusic import app
import re

BOT_USERNAME = "siyaprobot"


def stylize_text(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
        'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ',
        'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ',
        'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ',
        'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ',
        'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ',
        'Z': 'ᴢ',
    }
    return ''.join(small_caps.get(c, c) for c in text)


@app.on_message(filters.command(["stickerid","stid"]))
async def sticker_id(client, message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.reply_text(stylize_text("Please reply to a sticker."))
    else:
        st_in = message.reply_to_message.sticker
        await message.reply_text((f"""
⊹ <u>**Sᴛɪᴄᴋᴇʀ Iɴғᴏ**</u> ⊹
**⊚ Sᴛɪᴄᴋᴇʀ ID**: `{st_in.file_id}`

**⊚ Sᴛɪᴄᴋᴇʀ Uɴɪǫᴜᴇ ID**: `{st_in.file_unique_id}`
"""))


@app.on_message(filters.command("st"))
async def generate_sticker(client, message):
    if len(message.command) == 2:
        sticker_id = message.command[1]
        try:
            await client.send_sticker(message.chat.id, sticker=sticker_id)
        except Exception as e:
            await message.reply_text((f"Error: {e}"))
    else:
        await message.reply_text(stylize_text("Please provide a sticker ID after /st command."))


@app.on_message(filters.command("stdl") & filters.reply)
async def download_sticker(client, message):
    processing_msg = await message.reply_text(stylize_text("➣ Downloading Sticker..."))
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await processing_msg.edit_text(stylize_text("Please reply to a sticker!"))

    try:
        sticker = message.reply_to_message.sticker
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "sticker")
            await message.reply_to_message.download(file_path)

            if not sticker.is_animated and not sticker.is_video:
                processing_msg = await processing_msg.edit_text(stylize_text("➣ Processing Sticker..."))
                with Image.open(file_path) as img:
                    img.save(f"{file_path}.png", "PNG")
                await client.send_photo(
                    message.chat.id,
                    photo=f"{file_path}.png",
                    caption=stylize_text("Here's your sticker as an image!")
                )
            elif sticker.is_animated:
                processing_msg = await processing_msg.edit_text(stylize_text("➣ Sending Animated Sticker File..."))
                await client.send_document(
                    message.chat.id,
                    document=file_path,
                    caption=stylize_text("Here's your animated sticker file!")
                )
            elif sticker.is_video:
                processing_msg = await processing_msg.edit_text(stylize_text("➣ Sending Video Sticker..."))
                await client.send_video(
                    message.chat.id,
                    video=file_path,
                    supports_streaming=True,
                    caption=stylize_text("Here's your video sticker!")
                )

        await processing_msg.delete()
    except Exception as e:
        await processing_msg.edit_text(stylize_text(f"Error downloading sticker: {str(e)}"))



def clean_title(text: str) -> str:
    # Remove emojis and symbols except spaces and basic characters
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()[:64] or "My Sticker Pack"

@app.on_message(filters.command("packkang") & filters.reply)
async def pack_kang(client, message):
    processing_msg = await message.reply_text(stylize_text("➣ Pʀᴏᴄᴇssɪɴɢ..."))

    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await processing_msg.edit_text(stylize_text("Please reply to a sticker."))

    sticker = message.reply_to_message.sticker

    if not sticker.set_name:
        return await processing_msg.edit_text(stylize_text("This sticker is not part of any sticker pack."))

    try:
        # Fetch original sticker set
        sticker_set = await client.invoke(
            functions.messages.GetStickerSet(
                stickerset=types.InputStickerSetShortName(short_name=sticker.set_name),
                hash=0
            )
        )

        # Generate title and short_name
        raw_title = (
            f"{message.from_user.first_name}'s Sticker Pack by @{BOT_USERNAME}"
            if len(message.command) < 2
            else message.text.split(maxsplit=1)[1]
        )
        pack_name = clean_title(raw_title)
        short_name = f"pack_{uuid4().hex[:8]}_by_{BOT_USERNAME}"

        # Prepare sticker documents
        stickers = []
        for doc in sticker_set.documents:
            input_doc = types.InputDocument(
                id=doc.id,
                access_hash=doc.access_hash,
                file_reference=doc.file_reference,
            )
            emoji = next(
                (attr.alt for attr in doc.attributes if isinstance(attr, types.DocumentAttributeSticker)),
                "🎯"
            )
            stickers.append(
                types.InputStickerSetItem(
                    document=input_doc,
                    emoji=emoji
                )
            )

        user_peer = await client.resolve_peer(message.from_user.id)

        # Determine sticker type and create new set
        if sticker.is_animated:
            await client.invoke(
                functions.stickers.CreateStickerSetAnimated(
                    user_id=user_peer,
                    title=pack_name,
                    short_name=short_name,
                    stickers=stickers
                )
            )
        elif sticker.is_video:
            await client.invoke(
                functions.stickers.CreateStickerSetVideo(
                    user_id=user_peer,
                    title=pack_name,
                    short_name=short_name,
                    stickers=stickers
                )
            )
        else:
            await client.invoke(
                functions.stickers.CreateStickerSet(
                    user_id=user_peer,
                    title=pack_name,
                    short_name=short_name,
                    stickers=stickers
                )
            )

        await processing_msg.edit_text(
            stylize_text(f"✓ Sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ ᴄʟᴏɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!\n➥ Tᴏᴛᴀʟ sᴛɪᴄᴋᴇʀs: {len(stickers)}"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("↯ Vɪᴇᴡ Pᴀᴄᴋ", url=f"https://t.me/addstickers/{short_name}")
            ]])
        )

    except Exception as e:
        await processing_msg.edit_text(stylize_text(f"⚠️ Eʀʀᴏʀ: {str(e)}"))