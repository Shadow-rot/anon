from enum import Enum, auto
from AnonXMusic import app
from pyrogram.types import InlineKeyboardMarkup, Message
from AnonXMusic.utils.msg_types import button_markdown_parser
from AnonXMusic.utils.notes_func import NoteFillings
from emojis import decode


class FilterMessageTypeMap(Enum):
    text = auto()
    sticker = auto()
    animation = auto()
    document = auto()
    photo = auto()
    audio = auto()
    voice = auto()
    video = auto()
    video_note = auto()


async def SendFilterMessage(
    message: Message,
    filter_name: str,
    content: str,
    text: str,
    data_type: int,
    reply_markup=None
):
    chat_id = message.chat.id
    message_id = message.id

    if text:
        text = NoteFillings(message, text)

    try:
        if data_type == FilterMessageTypeMap.text.value:
            await app.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.sticker.value:
            await app.send_sticker(
                chat_id=chat_id,
                sticker=content,
                reply_to_message_id=message_id
            )

        elif data_type == FilterMessageTypeMap.animation.value:
            await app.send_animation(
                chat_id=chat_id,
                animation=content,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.document.value:
            await app.send_document(
                chat_id=chat_id,
                document=content,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.photo.value:
            await app.send_photo(
                chat_id=chat_id,
                photo=content,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.audio.value:
            await app.send_audio(
                chat_id=chat_id,
                audio=content,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.voice.value:
            await app.send_voice(
                chat_id=chat_id,
                voice=content,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.video.value:
            await app.send_video(
                chat_id=chat_id,
                video=content,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_type == FilterMessageTypeMap.video_note.value:
            await app.send_video_note(
                chat_id=chat_id,
                video_note=content,
                reply_to_message_id=message_id
            )
    except Exception as e:
        await message.reply(f"❌ Failed to send filter message: `{e}`")


async def GetFilterMessage(message: Message):
    data_type = None
    content = None
    text = ""

    raw_text = message.text or message.caption or ""

    if len(raw_text.split()) >= 3 and not message.reply_to_message:
        text = " ".join(raw_text.split()[2:])
        data_type = FilterMessageTypeMap.text.value

    elif message.reply_to_message:
        r = message.reply_to_message

        if r.text:
            text = r.text
            data_type = FilterMessageTypeMap.text.value

        elif r.sticker:
            content = r.sticker.file_id
            data_type = FilterMessageTypeMap.sticker.value

        elif r.animation:
            content = r.animation.file_id
            text = r.caption or ""
            data_type = FilterMessageTypeMap.animation.value

        elif r.document:
            content = r.document.file_id
            text = r.caption or ""
            data_type = FilterMessageTypeMap.document.value

        elif r.photo:
            content = r.photo.file_id
            text = r.caption or ""
            data_type = FilterMessageTypeMap.photo.value

        elif r.audio:
            content = r.audio.file_id
            text = r.caption or ""
            data_type = FilterMessageTypeMap.audio.value

        elif r.voice:
            content = r.voice.file_id
            text = r.caption or ""
            data_type = FilterMessageTypeMap.voice.value

        elif r.video:
            content = r.video.file_id
            text = r.caption or ""
            data_type = FilterMessageTypeMap.video.value

        elif r.video_note:
            content = r.video_note.file_id
            data_type = FilterMessageTypeMap.video_note.value

    return content, text, data_type


def get_text_reason(message: Message):
    text = decode(message.text)
    index_finder = [i for i in range(len(text)) if text[i] == '"']

    if len(index_finder) >= 2:
        query = text[index_finder[0] + 1:index_finder[1]]
        reason = text[index_finder[1] + 2:].strip() or None
    else:
        try:
            query = message.command[1]
            reason = ' '.join(message.command[2:]).strip() or None
        except IndexError:
            query = None
            reason = None

    return query, reason