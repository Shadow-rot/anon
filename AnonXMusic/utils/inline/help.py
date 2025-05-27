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
            [
                InlineKeyboardButton(text=_["H_B_17"], callback_data="help_callback hb17"),
                InlineKeyboardButton(text=_["H_B_18"], callback_data="help_callback hb18"),
                InlineKeyboardButton(text=_["H_B_19"], callback_data="help_callback hb19"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_20"], callback_data="help_callback hb20"),
                InlineKeyboardButton(text=_["H_B_21"], callback_data="help_callback hb21"),
                InlineKeyboardButton(text=_["H_B_22"], callback_data="help_callback hb22"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_23"], callback_data="help_callback hb23"),
                InlineKeyboardButton(text=_["H_B_24"], callback_data="help_callback hb24"),
                InlineKeyboardButton(text=_["H_B_25"], callback_data="help_callback hb25"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_26"], callback_data="help_callback hb26"),
                InlineKeyboardButton(text=_["H_B_27"], callback_data="help_callback hb27"),
                InlineKeyboardButton(text=_["H_B_28"], callback_data="help_callback hb28"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_29"], callback_data="help_callback hb29"),
                InlineKeyboardButton(text=_["H_B_30"], callback_data="help_callback hb30"),
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
@app.on_callback_query(filters.regex(r"help_callback hb([1-9]|1[0-9]|2[0-9]|30)"))
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
    "hb7": """
<u><b>ɢʟᴏʙᴀʟ ʙᴀɴ ғᴇᴀᴛᴜʀᴇ</b></u> [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :

/gban [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] : ɢʟᴏʙᴀʟʟʏ ʙᴀɴs ᴛʜᴇ ᴄʜᴜᴛɪʏᴀ ғʀᴏᴍ ᴀʟʟ ᴛʜᴇ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴀɴᴅ ʙʟᴀᴄᴋʟɪsᴛ ʜɪᴍ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.
/ungban [ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴜsᴇʀ] : ɢʟᴏʙᴀʟʟʏ ᴜɴʙᴀɴs ᴛʜᴇ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ᴜsᴇʀ.
/gbannedusers : sʜᴏᴡs ᴛʜᴇ ʟɪsᴛ ᴏғ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ᴜsᴇʀs.
""",
    "hb8": """
<b><u>ʟᴏᴏᴘ sᴛʀᴇᴀᴍ :</b></u>

<b>sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ ɪɴ ʟᴏᴏᴘ</b>

/loop [enable/disable] : ᴇɴᴀʙʟᴇs/ᴅɪsᴀʙʟᴇs ʟᴏᴏᴘ ғᴏʀ ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ
/loop [1, 2, 3, ...] : ᴇɴᴀʙʟᴇs ᴛʜᴇ ʟᴏᴏᴘ ғᴏʀ ᴛʜᴇ ɢɪᴠᴇɴ ᴠᴀʟᴜᴇ.
""",
    "hb9": """
<u><b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ</b></u> [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :

/logs : ɢᴇᴛ ʟᴏɢs ᴏғ ᴛʜᴇ ʙᴏᴛ.

/logger [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ʙᴏᴛ ᴡɪʟʟ sᴛᴀʀᴛ ʟᴏɢɢɪɴɢ ᴛʜᴇ ᴀᴄᴛɪᴠɪᴛɪᴇs ʜᴀᴩᴩᴇɴ ᴏɴ ʙᴏᴛ.

/maintenance [ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ] : ᴇɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴏғ ʏᴏᴜʀ ʙᴏᴛ.
""",
    "hb10": """
<b><u>ᴘɪɴɢ & sᴛᴀᴛs :</b></u>

/start : sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ.
/help : ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ ᴏғ ᴄᴏᴍᴍᴀɴᴅs.

/ping : sʜᴏᴡs ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ.

/stats : sʜᴏᴡs ᴛʜᴇ ᴏᴠᴇʀᴀʟʟ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ.
""",
    "hb11": """
<u><b>ᴩʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs :</b></u>

<b>v :</b> sᴛᴀɴᴅs ғᴏʀ ᴠɪᴅᴇᴏ ᴩʟᴀʏ.
<b>force :</b> sᴛᴀɴᴅs ғᴏʀ ғᴏʀᴄᴇ ᴩʟᴀʏ.

/play ᴏʀ /vplay : sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.

/playforce ᴏʀ /vplayforce : sᴛᴏᴩs ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ.
""",
    "hb12": """<b><u>sʜᴜғғʟᴇ ᴏ‌ᴜᴇᴜᴇ :</b></u>

/shuffle : sʜᴜғғʟᴇ's ᴛʜᴇ ᴏ‌ᴜᴇᴜᴇ.
/queue : sʜᴏᴡs ᴛʜᴇ sʜᴜғғʟᴇᴅ ᴏ‌ᴜᴇᴜᴇ.
""",
    "hb13": """<b><u>sᴇᴇᴋ sᴛʀᴇᴀᴍ :</b></u>
/seek [ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs] : sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ.
/seekback [ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs] : ʙᴀᴄᴋᴡᴀʀᴅ sᴇᴇᴋ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴛᴏ ᴛʜᴇ ᴛʜᴇ ɢɪᴠᴇɴ ᴅᴜʀᴀᴛɪᴏɴ.
""",
    "hb14": """<b><u>sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ</b></u>

/song [sᴏɴɢ ɴᴀᴍᴇ/ʏᴛ ᴜʀʟ] : ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴʏ ᴛʀᴀᴄᴋ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴍᴘ3 ᴏʀ ᴍᴘ4 ғᴏʀᴍᴀᴛs.
""",
    "hb15": """<b><u>sᴘᴇᴇᴅ ᴄᴏᴍᴍᴀɴᴅs :</b></u>

ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛʀᴏʟ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ ᴏғ ᴛʜᴇ ᴏɴɢᴏɪɴɢ sᴛʀᴇᴀᴍ. [ᴀᴅᴍɪɴs ᴏɴʟʏ]

/speed or /playback : ғᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ ᴛʜᴇ ᴀᴜᴅɪᴏ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ ɪɴ ɢʀᴏᴜᴘ.
/cspeed or /cplayback : ғᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ ᴛʜᴇ ᴀᴜᴅɪᴏ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ ɪɴ ᴄʜᴀɴɴᴇʟ.
""",
    "hb16": """<b><u>ᴀᴄᴛɪᴏɴs :</b></u>

ᴜsᴇ ᴛʜᴇsᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴍᴀɴᴀɢᴇ ᴜsᴇʀs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴩ.

/ban : ʙᴀɴ ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴩ.

/kick : ᴋɪᴄᴋ ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴩ.

/mute : ᴍᴜᴛᴇ ᴀ ᴜsᴇʀ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴩ.
""",
    "hb17": """<b><u>ᴛᴇxᴛ ᴇᴅɪᴛɪɴɢ :</b></u>

ᴜsᴇ ғᴏɴᴛs ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴛʏʟɪᴢᴇ ᴛᴇxᴛ.

/fonts <text> : ᴄᴏɴᴠᴇʀᴛ ᴛᴇxᴛ ɪɴᴛᴏ ᴄᴏᴏʟ ғᴏɴᴛ sᴛʏʟᴇs.
""",
    "hb18": """<b><u>ғᴜɴᴛᴀɢ :</b></u>

ᴛᴀɢ ᴜsᴇʀs ɪɴ ᴀ ғᴜɴ ᴡᴀʏ.

/gmtag /shayritag /lifetag /gntag : ᴛᴀɢ ᴍᴇᴍʙᴇʀs ᴡɪᴛʜ ᴅɪғғᴇʀᴇɴᴛ ᴍᴏᴏᴅs.
""",
    "hb19": """<b><u>ʜɪsᴛᴏʀʏ :</b></u>

ᴄʜᴇᴄᴋ ᴜsᴇʀ's ᴘᴀsᴛ ᴀᴄᴛɪᴠɪᴛʏ.

/sg : sʜᴏᴡ ᴜsᴇʀ ʜɪsᴛᴏʀʏ ʀᴇᴄᴏʀᴅ.
""",
    "hb20": """<b><u>ʟᴏᴄᴋs :</b></u>

ʟᴏᴄᴋ ᴄᴇʀᴛᴀɪɴ ᴛʏᴘᴇs ᴏғ ᴍᴇssᴀɢᴇs ɪɴ ɢʀᴏᴜᴩ.

/lock <type> : ʟᴏᴄᴋ ᴀɴʏᴛʜɪɴɢ (ᴇx: sᴛɪᴄᴋᴇʀs, ᴘʜᴏᴛᴏs, ʟɪɴᴋs).

/unlock <type> : ᴜɴʟᴏᴄᴋ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ.
""",
    "hb21": """<b><u>ᴋᴀɴɢ sᴛɪᴄᴋᴇʀ :</b></u>

ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ.

/kang : ᴋᴀɴɢ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ʏᴏᴜʀ ᴘᴀᴄᴋ.
""",
    "hb22": """<b><u>ɪɢ :</b></u>

ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs.

/ig <url> : ᴅᴏᴡɴʟᴏᴀᴅ ɪɢ ʀᴇᴇʟs ᴏʀ ᴠɪᴅᴇᴏs.
""",
    "hb23": """<b><u>ᴍᴀss ᴀᴄᴛɪᴏɴs :</b></u>

ᴘᴇʀғᴏʀᴍ ʙᴜʟᴋ ᴀᴄᴛɪᴏɴs (ᴏɴʟʏ ғᴏʀ ᴏᴡɴᴇʀ).

/banall : ʙᴀɴ ᴀʟʟ ᴍᴇᴍʙᴇʀs.

/kickall : ᴋɪᴄᴋ ᴀʟʟ ᴍᴇᴍʙᴇʀs.

/muteall : ᴍᴜᴛᴇ ᴀʟʟ ᴍᴇᴍʙᴇʀs.
""",
    "hb24": """<b><u>ᴡᴇʟᴄᴏᴍᴇ :</b></u>

sᴇɴᴅ ᴀ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ɴᴇᴡ ᴍᴇᴍʙᴇʀs.

/setwelcome : sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴛᴇxᴛ.

/delwelcome : ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴛᴇxᴛ.
""",
    "hb25": "Help for Module 25",
    "hb26": "Help for Module 26",
    "hb27": "Help for Module 27",
    "hb28": "Help for Module 28",
    "hb29": "Help for Module 29",
    "hb30": "Help for Module 30",
}

    help_text = help_texts.get(data, "Help not found.")

    await query.message.edit_text(
        text=help_text,
        reply_markup=help_back_markup({"BACK_BUTTON": "Back"})
    )