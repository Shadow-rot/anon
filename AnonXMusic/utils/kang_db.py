import os
from pyrogram import raw

def stylize_text(text):
    return text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    ))

def get_pack_name(user_id, sticker_type, pack_num):
    return f"user{user_id}_{sticker_type}pack{pack_num}_by_bot"

def get_pack_title(user_first_name, sticker_type, pack_num):
    return f"{user_first_name}'s {sticker_type.capitalize()} Sticker Pack {pack_num}"

async def upload_sticker(client, user_id, file_path, mime_type, sticker_type):
    attributes = [
        raw.types.DocumentAttributeFilename(file_name=os.path.basename(file_path)),
        raw.types.DocumentAttributeSticker(alt='', stickerset=raw.types.InputStickerSetEmpty(), mask=False)
    ]
    if sticker_type == "video":
        attributes.append(raw.types.DocumentAttributeVideo(duration=0, w=512, h=512, round_message=False, supports_streaming=False))

    media_file = await client.save_file(file_path)
    uploaded_media = await client.invoke(raw.functions.messages.UploadMedia(
        peer=await client.resolve_peer(user_id),
        media=raw.types.InputMediaUploadedDocument(file=media_file, mime_type=mime_type, attributes=attributes)
    ))
    return uploaded_media.document

async def create_sticker_pack(client, user_id, pack_name, pack_title, uploaded_document, emoji, sticker_type):
    try:
        input_sticker = raw.types.InputStickerSetItem(
            document=raw.types.InputDocument(
                id=uploaded_document.id,
                access_hash=uploaded_document.access_hash,
                file_reference=uploaded_document.file_reference
            ),
            emoji=emoji
        )

        kwargs = dict(
            user_id=await client.resolve_peer(user_id),  # No need to check interaction
            title=pack_title,
            short_name=pack_name,
            stickers=[input_sticker],
            masks=False
        )

        if sticker_type == "animated":
            kwargs["animated"] = True
        elif sticker_type == "video":
            kwargs["videos"] = True

        await client.invoke(raw.functions.stickers.CreateStickerSet(**kwargs))

    except Exception as e:
        print(f"Failed to create sticker pack: {e}")  # Just log the error, no need to notify users

async def send_pack_message(msg, is_new, sticker_type, pack_title, pack_name, sticker_count, emoji):
    text = f"**➣ {'Created a new' if is_new else 'Added to'} {sticker_type.capitalize()} Pack!**\n\n"
    text += f"Pack ➣ `{pack_title}`\nStickers ➣ `{sticker_count}`\nEmoji ➣ `{emoji}`"
    await msg.edit(stylize_text(text), reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("View Pack", url=f"https://t.me/addstickers/{pack_name}")]
    ]))