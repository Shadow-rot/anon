import os
import tempfile
import shutil
import subprocess
import traceback
from pyrogram import Client, filters, raw
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import StickersetInvalid, StickersTooMuch, StickerEmojiInvalid, FloodWait, FileReferenceExpired, RPCError
from PIL import Image

from AnonXMusic import app

BOT_USERNAME = "lovely_xu_bot"

# Convert text to small caps
def stylize_text(text):
    small_caps = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    )
    return text.translate(small_caps)

# Generate pack name
def get_pack_name(user_id, is_animated, is_video, pack_num):
    return f"user{user_id}_{'animated' if is_animated else 'video' if is_video else 'regular'}pack{pack_num}_by_{BOT_USERNAME.lower()}"

# Generate pack title
def get_pack_title(user_first_name, is_animated, is_video, pack_num):
    return f"{user_first_name}'s {'Animated' if is_animated else 'Video' if is_video else 'Sticker'} Pack {pack_num}"

# Send success message with pack link
async def send_pack_message(msg, is_new, type_of_pack, pack_title, pack_name, sticker_count, emoji):
    text = f"**➣ {'Created a new' if is_new else 'Added to your existing'} {type_of_pack} pack!**\n\n"
    text += f"Pack ➣ `{pack_title}`\nStickers ➣ `{sticker_count}`\nEmoji ➣ `{emoji}`"
    await msg.edit(stylize_text(text), reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("View Pack", url=f"https://t.me/addstickers/{pack_name}")]
    ]))

# Upload sticker file
async def upload_sticker_file(client, user_id, media, is_animated, is_video):
    mime_type = "application/x-tgsticker" if is_animated else "video/webm" if is_video else "image/png"
    file_name = "sticker.tgs" if is_animated else "sticker.webm" if is_video else "sticker.png"

    attributes = [
        raw.types.DocumentAttributeFilename(file_name=file_name),
        raw.types.DocumentAttributeSticker(alt='', stickerset=raw.types.InputStickerSetEmpty(), mask=False)
    ]
    if is_video:
        attributes.append(raw.types.DocumentAttributeVideo(duration=0, w=512, h=512, round_message=False, supports_streaming=False))

    media_file = await client.save_file(media)
    uploaded_media = await client.invoke(raw.functions.messages.UploadMedia(
        peer=await client.resolve_peer(user_id),
        media=raw.types.InputMediaUploadedDocument(file=media_file, mime_type=mime_type, attributes=attributes)
    ))
    return uploaded_media.document

# Create a new sticker pack
async def create_sticker_pack(client, user_id, pack_name, pack_title, uploaded_document, emoji, is_animated, is_video):
    await client.invoke(raw.functions.stickers.CreateStickerSet(
        user_id=await client.resolve_peer(user_id),
        title=pack_title,
        short_name=pack_name,
        stickers=[raw.types.InputStickerSetItem(document=raw.types.InputDocument(
            id=uploaded_document.id, access_hash=uploaded_document.access_hash, file_reference=uploaded_document.file_reference), emoji=emoji)],
        animated=is_animated,
        videos=is_video
    ))

# Kang command
@app.on_message(filters.command("kang") & filters.reply)
async def kang(client, message):
    msg = await message.reply_text(stylize_text("➣ Processing..."))
    reply, user = message.reply_to_message, message.from_user
    user_id, user_first_name = user.id, user.first_name

    if not reply or not (reply.sticker or reply.photo or reply.animation or reply.document or reply.video):
        return await msg.edit(stylize_text("Reply to a sticker, photo, GIF, or video to kang it!"))

    emoji = message.command[1] if len(message.command) > 1 else "🤔"
    is_animated = reply.sticker and reply.sticker.is_animated if reply.sticker else False
    is_video = reply.sticker and reply.sticker.is_video if reply.sticker else (reply.video or (reply.document and reply.document.mime_type.startswith('video/')))
    
    temp_dir, media = tempfile.mkdtemp(), None
    try:
        file_path = os.path.join(temp_dir, "kang_sticker.tgs" if is_animated else "kang_sticker.webm" if is_video else "kang_sticker.png")
        await reply.download(file_path)

        if reply.photo or (reply.document and "image" in reply.document.mime_type):
            img = Image.open(file_path)
            img.thumbnail((512, 512), Image.LANCZOS)
            img.convert("RGBA").save(file_path, "PNG")
        
        elif reply.video or (reply.document and "video" in reply.document.mime_type):
            output_path = os.path.join(temp_dir, "kang_sticker.webm")
            subprocess.run([
                'ffmpeg', '-y', '-i', file_path, '-vf', 'scale=512:512:flags=lanczos:force_original_aspect_ratio=decrease',
                '-ss', '0', '-t', '3', '-c:v', 'libvpx-vp9', '-b:v', '500k', '-crf', '30', '-an', '-r', '30', output_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            file_path = output_path

        media = file_path
        type_of_pack = 'Animated' if is_animated else 'Video' if is_video else 'Static'
        pack_num, max_stickers = 0, 50 if is_animated or is_video else 120

        while True:
            pack_name = get_pack_name(user_id, is_animated, is_video, pack_num)
            try:
                sticker_set = await client.invoke(raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name), hash=0))
                if len(sticker_set.documents) >= max_stickers:
                    pack_num += 1
                    continue
                break
            except StickersetInvalid:
                break

        pack_title = get_pack_title(user_first_name, is_animated, is_video, pack_num)
        uploaded_document = await upload_sticker_file(client, user_id, media, is_animated, is_video)

        try:
            await client.invoke(raw.functions.stickers.AddStickerToSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                sticker=raw.types.InputStickerSetItem(document=raw.types.InputDocument(
                    id=uploaded_document.id, access_hash=uploaded_document.access_hash, file_reference=uploaded_document.file_reference), emoji=emoji)
            ))
            sticker_set = await client.invoke(raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=pack_name), hash=0))
            await send_pack_message(msg, False, type_of_pack, pack_title, pack_name, len(sticker_set.documents), emoji)
        except StickersTooMuch:
            await create_sticker_pack(client, user_id, pack_name, pack_title, uploaded_document, emoji, is_animated, is_video)
            await send_pack_message(msg, True, type_of_pack, pack_title, pack_name, 1, emoji)
    except Exception as e:
        await msg.edit(f"Error: {traceback.format_exc()}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)