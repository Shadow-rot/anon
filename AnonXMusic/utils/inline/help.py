from typing import Union
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from AnonXMusic import app
from strings import (
    HELP_1, HELP_2, HELP_3, HELP_4,
    HELP_5, HELP_6, HELP_7, HELP_8,
    HELP_9, HELP_10, HELP_11, HELP_12,
    HELP_13, HELP_14, HELP_15, HELP_16,
)


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
@app.on_callback_query(filters.regex(r"help_callback_hb(1[0-6]|[1-9])"))
async def help_button_handler(_, query: CallbackQuery):
    data = query.data.replace("help_callback_", "")

    help_texts = {
        "hb1": HELP_1,
        "hb2": HELP_2,
        "hb3": HELP_3,
        "hb4": HELP_4,
        "hb5": HELP_5,
        "hb6": HELP_6,
        "hb7": HELP_7,
        "hb8": HELP_8,
        "hb9": HELP_9,
        "hb10": HELP_10,
        "hb11": HELP_11,
        "hb12": HELP_12,
        "hb13": HELP_13,
        "hb14": HELP_14,
        "hb15": HELP_15,
        "hb16": HELP_16,
    }

    help_text = help_texts.get(data, "Help not found.")

    await query.message.edit_text(
        text=help_text,
        reply_markup=help_back_markup({"BACK_BUTTON": "Back"})
    )