import imghdr
import os
from asyncio import gather
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import (
    PeerIdInvalid,
    ShortnameOccupyFailed,
    StickerEmojiInvalid,
    StickerPngDimensions,
    StickerPngNopng,
    UserIsBlocked,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from AnonXMusic import app
from config import BOT_USERNAME
from AnonXMusic.utils.errors import capture_err
from AnonXMusic.utils.files import (
    get_document_from_file_id,
    resize_file_to_sticker_size,
    upload_document,
)
from AnonXMusic.utils.stickerset import (
    add_sticker_to_set,
    create_sticker,
    create_sticker_set,
    get_sticker_set_by_name,
)

MAX_STICKERS = 120
SUPPORTED_TYPES = ["jpeg", "png", "webp"]

# Clean bot username for pack naming
botname_clean = BOT_USERNAME.replace("@", "")

@app.on_message(filters.command("get_sticker"))
@capture_err
async def sticker_image(_, message: Message):
    r = message.reply_to_message
    if not r or not r.sticker:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ......")

    m = await message.reply("sᴇɴᴅɪɴɢ.........ᴡᴀɪᴛ")
    f = await r.download(f"{r.sticker.file_unique_id}.png")

    await gather(
        message.reply_photo(f),
        message.reply_document(f),
    )

    await m.delete()
    os.remove(f)


@app.on_message(filters.command("kang"))
@capture_err
async def kang(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ/ɪᴍᴀɢᴇ ᴛᴏ ᴋᴀɴɢ ᴛʜᴀᴛ...")
    if not message.from_user:
        return await message.reply_text("ʏᴏᴜ ᴀʀᴇ ᴀɴᴏɴ ᴀᴅᴍɪɴ, ᴋᴀɴɢ sᴛɪᴄᴋᴇʀs ɪɴ ᴍʏ ᴘᴍ.....")

    msg = await message.reply_text("ᴋᴀɴɢɪɴɢ sᴛɪᴄᴋᴇʀ.....")

    args = message.text.split()
    if len(args) > 1:
        sticker_emoji = str(args[1])
    elif message.reply_to_message.sticker and message.reply_to_message.sticker.emoji:
        sticker_emoji = message.reply_to_message.sticker.emoji
    else:
        sticker_emoji = "🤔"

    doc = message.reply_to_message.photo or message.reply_to_message.document

    try:
        if message.reply_to_message.sticker:
            sticker = await create_sticker(
                await get_document_from_file_id(message.reply_to_message.sticker.file_id),
                sticker_emoji,
            )
        elif doc:
            if doc.file_size > 10_000_000:
                return await msg.edit("ғɪʟᴇ sɪᴢᴇs ᴛᴏᴏ ʟᴀʀɢᴇ.")

            temp_file_path = await app.download_media(doc)
            image_type = imghdr.what(temp_file_path)

            if image_type not in SUPPORTED_TYPES:
                return await msg.edit(f"ғᴏʀᴍᴀᴛ ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ! ({image_type})")

            try:
                temp_file_path = await resize_file_to_sticker_size(temp_file_path)
            except OSError as e:
                await msg.edit("Something went wrong while resizing the image.")
                raise Exception(f"ʀᴇsɪᴢᴇ ғᴀɪʟᴇᴅ ᴀᴛ {temp_file_path}; {e}")

            sticker = await create_sticker(
                await upload_document(client, temp_file_path, message.chat.id),
                sticker_emoji,
            )

            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)
        else:
            return await msg.edit("ᴄᴀɴ'ᴛ ᴋᴀɴɢ ᴛʜɪs ᴍᴇssᴀɢᴇ....")
    except ShortnameOccupyFailed:
        return await message.reply_text("Change your name or username.")
    except Exception as e:
        await message.reply_text(str(e))
        print(format_exc())
        return

    packnum = 0
    base_packname = f"f{message.from_user.id}_by_{botname_clean}"
    packname = base_packname
    limit = 0

    try:
        while True:
            if limit >= 50:
                return await msg.delete()

            stickerset = await get_sticker_set_by_name(client, packname)

            if not stickerset:
                await create_sticker_set(
                    client,
                    message.from_user.id,
                    f"{message.from_user.first_name[:32]}'s kang pack",
                    packname,
                    [sticker],
                )
            elif stickerset.set.count >= MAX_STICKERS:
                packnum += 1
                packname = f"f{packnum}_{message.from_user.id}_by_{botname_clean}"
                limit += 1
                continue
            else:
                try:
                    await add_sticker_to_set(client, stickerset, sticker)
                except StickerEmojiInvalid:
                    return await msg.edit("[ERROR]: Invalid emoji in argument.")
            break

        await msg.edit(
            "sᴛɪᴄᴋᴇʀ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴘᴀᴄᴋ!\nᴛᴀᴘ ᴛʜᴇ ʙᴜᴛᴛᴏɴ",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View Pack", url=f"https://t.me/addstickers/{packname}")]
            ])
        )

    except (PeerIdInvalid, UserIsBlocked):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Start", url=f"https://t.me/{botname_clean}")]
        ])
        await msg.edit(
            "ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ sᴛᴀʀᴛ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴡɪᴛʜ ᴍᴇ...",
            reply_markup=keyboard,
        )
    except StickerPngNopng:
        await message.reply_text("Stickers must be PNG files, but this one is not.")
    except StickerPngDimensions:
        await message.reply_text("The sticker PNG dimensions are invalid.")