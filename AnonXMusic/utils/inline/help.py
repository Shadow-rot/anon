from typing import Union
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from AnonXMusic import app  # your Pyrogram Client

# Dummy help strings (replace with your actual ones)
HELP_1 = "Help section 1"
HELP_2 = "Help section 2"
HELP_3 = "Help section 3"
HELP_4 = "Help section 4"
HELP_5 = "Help section 5"
HELP_6 = "Help section 6"
HELP_7 = "Help section 7"
HELP_8 = "Help section 8"
HELP_9 = "Help section 9"
HELP_10 = "Help section 10"
HELP_11 = "Help section 11"
HELP_12 = "Help section 12"
HELP_13 = "Help section 13"
HELP_14 = "Help section 14"
HELP_15 = "Help section 15"
HELP_16 = "Help section 16"

# Dummy language dict
_ = {
    "CLOSE_BUTTON": "Close",
    "BACK_BUTTON": "Back",
    "H_B_1": "Help 1", "H_B_2": "Help 2", "H_B_3": "Help 3",
    "H_B_4": "Help 4", "H_B_5": "Help 5", "H_B_6": "Help 6",
    "H_B_7": "Help 7", "H_B_8": "Help 8", "H_B_9": "Help 9",
    "H_B_10": "Help 10", "H_B_11": "Help 11", "H_B_12": "Help 12",
    "H_B_13": "Help 13", "H_B_14": "Help 14", "H_B_15": "Help 15", "H_B_16": "Help 16",
    "S_B_4": "Get Help",
}

def help_panel(START: Union[bool, int] = None):
    first = [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
    second = [InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_back_helper")]
    mark = second if START else first

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_1"], callback_data="help_hb1"),
                InlineKeyboardButton(text=_["H_B_2"], callback_data="help_hb2"),
                InlineKeyboardButton(text=_["H_B_3"], callback_data="help_hb3"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_4"], callback_data="help_hb4"),
                InlineKeyboardButton(text=_["H_B_5"], callback_data="help_hb5"),
                InlineKeyboardButton(text=_["H_B_6"], callback_data="help_hb6"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_7"], callback_data="help_hb7"),
                InlineKeyboardButton(text=_["H_B_8"], callback_data="help_hb8"),
                InlineKeyboardButton(text=_["H_B_9"], callback_data="help_hb9"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_10"], callback_data="help_hb10"),
                InlineKeyboardButton(text=_["H_B_11"], callback_data="help_hb11"),
                InlineKeyboardButton(text=_["H_B_12"], callback_data="help_hb12"),
            ],
            [
                InlineKeyboardButton(text=_["H_B_13"], callback_data="help_hb13"),
                InlineKeyboardButton(text=_["H_B_14"], callback_data="help_hb14"),
                InlineKeyboardButton(text=_["H_B_15"], callback_data="help_hb15"),
                InlineKeyboardButton(text=_["H_B_16"], callback_data="help_hb16"),
            ],
            mark,
        ]
    )

def help_back_markup():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_back_helper")]]
    )

# Show help panel with command
@app.on_message(filters.command("help"))
async def help_command(_, message: Message):
    await message.reply_text(
        "Select a help category below:",
        reply_markup=help_panel(),
    )

# Callback query handler
@app.on_callback_query(filters.regex(r"help_hb(1[0-6]|[1-9])"))
async def help_button_handler(_, query: CallbackQuery):
    data = query.data.replace("help_", "")

    help_texts = {
        "hb1": HELP_1, "hb2": HELP_2, "hb3": HELP_3, "hb4": HELP_4,
        "hb5": HELP_5, "hb6": HELP_6, "hb7": HELP_7, "hb8": HELP_8,
        "hb9": HELP_9, "hb10": HELP_10, "hb11": HELP_11, "hb12": HELP_12,
        "hb13": HELP_13, "hb14": HELP_14, "hb15": HELP_15, "hb16": HELP_16,
    }

    await query.message.edit_text(
        text=help_texts.get(data, "Help not found."),
        reply_markup=help_back_markup()
    )