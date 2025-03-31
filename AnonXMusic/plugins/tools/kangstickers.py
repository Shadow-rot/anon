import os
import tempfile
import shutil
import subprocess
import traceback
from pyrogram import Client, filters, raw
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import StickersetInvalid, StickersTooMuch, FloodWait, RPCError, PeerIdInvalid
from PIL import Image

from config import BOT_USERNAME
from AnonXMusic.utils.kang_db import stylize_text, get_pack_name, get_pack_title, upload_sticker, create_sticker_pack, send_pack_message

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
    sticker_type = "animated" if is_animated else "video" if is_video else "regular"

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, f"sticker.{ 'tgs' if is_animated else 'webm' if is_video else 'png' }")

    try:
        await reply.download(file_path)

        if reply.photo or (reply.document and "image" in reply.document.mime_type):
            img = Image.open(file_path)
            img.thumbnail((512, 512), Image.LANCZOS)
            img.convert("RGBA").save(file_path, "PNG")

        elif is_video:
            output_path = os.path.join(temp_dir, "sticker.webm")
            subprocess.run([
                'ffmpeg', '-y', '-i', file_path, '-vf', 'scale=512:512:flags=lanczos:force_original_aspect_ratio=decrease',
                '-t', '3', '-c:v', 'libvpx-vp9', '-b:v', '500k', '-crf', '30', '-an', '-r', '30', output_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            file_path = output_path

        pack_num, max_stickers = 0, 50 if is_animated or is_video else 120

        while True:
            pack_name = get_pack_name(user_id, sticker_type, pack_num)

            try:
                sticker_set = await client.invoke(raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name), hash=0))

                if len(sticker_set.documents) >= max_stickers:
                    pack_num += 1
                    continue
                break
            except StickersetInvalid:
                sticker_set = None
                break

        pack_title = get_pack_title(user_first_name, sticker_type, pack_num)
        mime_type = "application/x-tgsticker" if is_animated else "video/webm" if is_video else "image/png"
        uploaded_document = await upload_sticker(client, user_id, file_path, mime_type, sticker_type)

        if sticker_set is None:
            await create_sticker_pack(client, user_id, pack_name, pack_title, uploaded_document, emoji, sticker_type)
            await send_pack_message(msg, True, sticker_type, pack_title, pack_name, 1, emoji)
        else:
            try:
                await client.invoke(raw.functions.stickers.AddStickerToSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name),
                    sticker=raw.types.InputStickerSetItem(
                        document=raw.types.InputDocument(
                            id=uploaded_document.id, access_hash=uploaded_document.access_hash, file_reference=uploaded_document.file_reference),
                        emoji=emoji
                    )
                ))
                sticker_set = await client.invoke(raw.functions.messages.GetStickerSet(
                    stickerset=raw.types.InputStickerSetShortName(short_name=pack_name), hash=0))
                await send_pack_message(msg, False, sticker_type, pack_title, pack_name, len(sticker_set.documents), emoji)
            except StickersTooMuch:
                pack_num += 1
                pack_name = get_pack_name(user_id, sticker_type, pack_num)
                pack_title = get_pack_title(user_first_name, sticker_type, pack_num)
                await create_sticker_pack(client, user_id, pack_name, pack_title, uploaded_document, emoji, sticker_type)
                await send_pack_message(msg, True, sticker_type, pack_title, pack_name, 1, emoji)

    except Exception:
        await msg.edit(f"Error:\n`{traceback.format_exc()}`")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)