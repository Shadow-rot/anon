from enum import Enum, auto
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup
from AnonXMusic import app
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


def get_text_reason(message: Message):
    """Extract filter name and optional reason/content from user input"""
    text = decode(message.text or "")
    index_finder = [i for i, char in enumerate(text) if char == '"']

    if len(index_finder) >= 2:
        name = text[index_finder[0] + 1: index_finder[1]]
        reason = text[index_finder[1] + 2:].strip() or None
    else:
        # Safely access command args
        if not message.command or len(message.command) < 2:
            return None, None  # or raise an error, or handle accordingly
        name = message.command[1]
        reason = " ".join(message.command[2:]) or None

    return name, reason


async def GetFIlterMessage(message: Message):
    msg = message.reply_to_message
    data_type = None
    content = None
    text = ""

    raw_text = message.text or message.caption or ""
    args = raw_text.split(None, 2)

    if not msg and len(args) >= 3:
        text = args[2]
        data_type = FilterMessageTypeMap.text.value

    elif msg:
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
            data_type = FilterMessageTypeMap.video_note.value

    return content, text, data_type


async def SendFilterMessage(message: Message, filter_name: str, content: str, text: str, data_type: int):
    chat_id = message.chat.id
    reply_id = message.id

    text = text or ""
    text, buttons = button_markdown_parser(text)
    text = NoteFillings(message, text)

    valid_buttons = []
    for row in buttons:
        filtered_row = []
        for btn in row:
            if hasattr(btn, "url") and btn.url and not btn.url.startswith(("http://", "https://")):
                continue  # Skip invalid URLs
            filtered_row.append(btn)
        if filtered_row:
            valid_buttons.append(filtered_row)

    reply_markup = InlineKeyboardMarkup(valid_buttons) if valid_buttons else None

    try:
        if data_type == FilterMessageTypeMap.text.value:
            await app.send_message(chat_id, text=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.sticker.value:
            await app.send_sticker(chat_id, sticker=content, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.animation.value:
            await app.send_animation(chat_id, animation=content, caption=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.document.value:
            await app.send_document(chat_id, document=content, caption=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.photo.value:
            await app.send_photo(chat_id, photo=content, caption=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.audio.value:
            await app.send_audio(chat_id, audio=content, caption=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.voice.value:
            await app.send_voice(chat_id, voice=content, caption=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.video.value:
            await app.send_video(chat_id, video=content, caption=text, reply_markup=reply_markup, reply_to_message_id=reply_id)
        elif data_type == FilterMessageTypeMap.video_note.value:
            await app.send_video_note(chat_id, video_note=content, reply_markup=reply_markup, reply_to_message_id=reply_id)

    except Exception as e:
        await message.reply(
            f"<b>Failed to send filter:</b>\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
            quote=True,
        )