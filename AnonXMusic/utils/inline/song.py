from pyrogram.types import InlineKeyboardButton

def song_markup(_, video_id: str):
    return [
        [
            InlineKeyboardButton(text="🎵 Audio", callback_data=f"song_helper audio|{video_id}"),
            InlineKeyboardButton(text="🎬 Video", callback_data=f"song_helper video|{video_id}"),
        ],
        [
            InlineKeyboardButton(text="✖️ Close", callback_data="close")
        ]
    ]