from typing import Union
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from AnonXMusic import app


def help_pannel(_, START: Union[bool, int] = None):
    first = [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
    second = [
        InlineKeyboardButton(
            text=_["BACK_BUTTON"],
            callback_data="settingsback_helper",
        ),
    ]
    mark = second if START else first
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_1"], callback_data="help_callback hb1"),
                InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2"),
                InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4"),
                InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5"),
                InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7"),
                InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8"),
                InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10"),
                InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11"),
                InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13"),
                InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14"),
                InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15"),
                InlineKeyboardButton(text=_["H_B_16"], callback_data="help_callback hb16"),
            ],
            mark,
        ]
    )
    return upl


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
            ),
        ],
    ]
    return buttons


# Handler for all 16 help buttons
@app.on_callback_query(filters.regex(r"help_callback hb(1[0-6]|[1-9])"))
async def help_button_handler(_, query: CallbackQuery):
    data = query.data.split()[1]

    help_texts = {
    "hb1": """<b><u>ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs :</b></u>

ᴊᴜsᴛ ᴀᴅᴅ <b>ᴄ</b> ɪɴ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴜsᴇ ᴛʜᴇᴍ ғᴏʀ ᴄʜᴀɴɴᴇʟ.

/pause : ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.
/resume : ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ.
/skip : sᴋɪᴩ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ.
/end ᴏʀ /stop : ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅs ᴛʜᴇ sᴛʀᴇᴀᴍ.
/player : ɢᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩʟᴀʏᴇʀ ᴩᴀɴᴇʟ.
/queue : sʜᴏᴡs ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs.
""",
    "hb2": """
<b><u>ᴀᴜᴛʜ ᴜsᴇʀs :</b></u>

ᴀᴜᴛʜ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴛʜᴇ ʙᴏᴛ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.

/auth [ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ] : ᴀᴅᴅ ᴀ ᴜsᴇʀ ᴛᴏ ᴀᴜᴛʜ ʟɪsᴛ.
/unauth [ᴜsᴇʀɴᴀᴍᴇ/ᴜsᴇʀ_ɪᴅ] : ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴀᴜᴛʜ ʟɪsᴛ.
/authusers : sʜᴏᴡ ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ.
""",
    "hb3": """
<u><b>ʙʀᴏᴀᴅᴄᴀsᴛ ғᴇᴀᴛᴜʀᴇ</b></u> [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :

/broadcast [ᴍᴇssᴀɢᴇ/ʀᴇᴩʟʏ] : sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs.

<b>ᴍᴏᴅᴇs:</b>
- <b>pin</b>: ᴩɪɴ ᴛᴏ ᴄʜᴀᴛs
- <b>pinloud</b>: ᴩɪɴ + ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ
- <b>user</b>: sᴇɴᴅ ᴛᴏ sᴛᴀʀᴛᴇᴅ ᴜsᴇʀs
- <b>assistant</b>: sᴇɴᴅ ᴠɪᴀ ᴀssɪsᴛᴀɴᴛ
- <b>nobot</b>: sᴋɪᴩ ʙᴏᴛ

<b>ᴇxᴀᴍᴩʟᴇ:</b> <code>/broadcast -user -assistant -pin ᴛᴇsᴛ</code>
""",
    "hb4": """<u><b>ᴄʜᴀᴛ ʙʟᴀᴄᴋʟɪsᴛ :</b></u> [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs]

/blacklistchat [ᴄʜᴀᴛ_ɪᴅ] : ʙʟᴏᴄᴋ ᴀ ᴄʜᴀᴛ.
/whitelistchat [ᴄʜᴀᴛ_ɪᴅ] : ᴜɴʙʟᴏᴄᴋ ᴀ ᴄʜᴀᴛ.
/blacklistedchat : ʟɪsᴛ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ ᴄʜᴀᴛs.
""",
    "hb5": """
<u><b>ʙʟᴏᴄᴋ ᴜsᴇʀs:</b></u> [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs]

/block [ᴜsᴇʀɴᴀᴍᴇ/ʀᴇᴩʟʏ] : ʙʟᴏᴄᴋ ᴛʜᴇ ᴜsᴇʀ.
/unblock [ᴜsᴇʀɴᴀᴍᴇ/ʀᴇᴩʟʏ] : ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ᴜsᴇʀ.
/blockedusers : sʜᴏᴡ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs.
""",
    "hb6": """
<u><b>ᴄʜᴀɴɴᴇʟ ᴩʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs:</b></u>

ᴇɴᴀʙʟᴇᴅ ᴛᴏ ᴘʟᴀʏ ᴍᴜsɪᴄ ɪɴ ᴄʜᴀɴɴᴇʟs ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.

/cplay : ᴘʟᴀʏ ᴛʀᴀᴄᴋ ɪɴ ᴄʜᴀɴɴᴇʟ.
/cpause : ᴩᴀᴜsᴇ ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ.
/cresume : ʀᴇsᴜᴍᴇ ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ.
/cend : sᴛᴏᴘ ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ.
""",
    "hb7": "Help for Module 7",
    "hb8": "Help for Module 8",
    "hb9": "Help for Module 9",
    "hb10": "Help for Module 10",
    "hb11": "Help for Module 11",
    "hb12": "Help for Module 12",
    "hb13": "Help for Module 13",
    "hb14": "Help for Module 14",
    "hb15": "Help for Module 15",
    "hb16": "Help for Module 16",
}

    help_text = help_texts.get(data, "Help not found.")

    await query.message.edit_text(
        text=help_text,
        reply_markup=help_back_markup({"BACK_BUTTON": "Back"})
    )