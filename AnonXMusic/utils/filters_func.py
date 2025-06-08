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


async def SendFilterMessage(message: Message, filter_name: str, content: str, text: str, data_type: int):
    chat_id = message.chat.id
    message_id = message.id

    # Parse buttons from markdown text
    text, buttons = button_markdown_parser(text or "")
    text = NoteFillings(message, text or "")
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    # Send correct media type
    if data_type == FilterMessageTypeMap.text.value:
        await app.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.sticker.value:
        await app.send_sticker(
            chat_id=chat_id,
            sticker=content,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.animation.value:
        await app.send_animation(
            chat_id=chat_id,
            animation=content,
            caption=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.document.value:
        await app.send_document(
            chat_id=chat_id,
            document=content,
            caption=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.photo.value:
        await app.send_photo(
            chat_id=chat_id,
            photo=content,
            caption=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.audio.value:
        await app.send_audio(
            chat_id=chat_id,
            audio=content,
            caption=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.voice.value:
        await app.send_voice(
            chat_id=chat_id,
            voice=content,
            caption=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.video.value:
        await app.send_video(
            chat_id=chat_id,
            video=content,
            caption=text,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )

    elif data_type == FilterMessageTypeMap.video_note.value:
        await app.send_video_note(
            chat_id=chat_id,
            video_note=content,
            reply_markup=reply_markup,
            reply_to_message_id=message_id
        )


async def GetFIlterMessage(message: Message):
    data_type = None
    content = None
    text = ""

    raw_text = message.text or message.caption
    args = raw_text.split(None, 2)

    if len(args) >= 3 and not message.reply_to_message:
        text = raw_text[len(args[0]) + len(args[1]) + 2:].strip()
        data_type = FilterMessageTypeMap.text.value

    if message.reply_to_message:
        msg = message.reply_to_message

        if msg.text:
            text = msg.text
            data_type = FilterMessageTypeMap.text.value

        elif msg.sticker:
            content = msg.sticker.file_id
            data_type = FilterMessageTypeMap.sticker.value

        elif msg.animation:
            content = msg.animation.file_id
            text = msg.caption or ""
            data_type = FilterMessageTypeMap.animation.value

        elif msg.document:
            content = msg.document.file_id
            text = msg.caption or ""
            data_type = FilterMessageTypeMap.document.value

        elif msg.photo:
            content = msg.photo.file_id
            text = msg.caption or ""
            data_type = FilterMessageTypeMap.photo.value

        elif msg.audio:
            content = msg.audio.file_id
            text = msg.caption or ""
            data_type = FilterMessageTypeMap.audio.value

        elif msg.voice:
            content = msg.voice.file_id
            text = msg.caption or ""
            data_type = FilterMessageTypeMap.voice.value

        elif msg.video:
            content = msg.video.file_id
            text = msg.caption or ""
            data_type = FilterMessageTypeMap.video.value

        elif msg.video_note:
            content = msg.video_note.file_id
            text = ""
            data_type = FilterMessageTypeMap.video_note.value

    return content, text, data_type


def get_text_reason(message: Message):
    text = decode(message.text)
    index_finder = [x for x in range(len(text)) if text[x] == '"']

    if len(index_finder) >= 2:
        filter_name = text[index_finder[0]+1:index_finder[1]]
        reason = text[index_finder[1]+2:] or None
    else:
        filter_name = message.command[1]
        reason = ' '.join(message.command[2:]) or None

    return filter_name, reason