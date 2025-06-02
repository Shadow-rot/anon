import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

LOVE_GIFS = [
    "https://media.tenor.com/BuzXvIh2NUgAAAAC/anime-love.gif",
    "https://media.tenor.com/jkP3zRP5yU8AAAAC/love-hearts.gif",
    "https://media.tenor.com/XM59c1V50vMAAAAC/love-anime.gif",
    "https://media.tenor.com/7yfpAmV4P1EAAAAC/couple-anime.gif",
    "https://media.tenor.com/jk7JhYJJmPwAAAAC/anime-hug-love.gif"
]

def get_random_message(love_percentage: int) -> str:
    if love_percentage <= 30:
        return random.choice([
            "💔 Lᴏᴠᴇ ɪs ɪɴ ᴛʜᴇ ᴀɪʀ, ʙᴜᴛ ɪᴛ ɴᴇᴇᴅs ᴀ ʟɪᴛᴛʟᴇ ꜱᴘᴀʀᴋ!",
            "🌱 A ɢᴏᴏᴅ sᴛᴀʀᴛ, ʙᴜᴛ ᴛʜᴇʀᴇ's ʀᴏᴏᴍ ᴛᴏ ɢʀᴏᴡ.",
            "💫 Jᴜsᴛ ᴛʜᴇ ʙᴇɢɪɴɴɪɴɢ ᴏғ sᴏᴍᴇᴛʜɪɴɢ ʙᴇᴀᴜᴛɪғᴜʟ.",
        ])
    elif love_percentage <= 70:
        return random.choice([
            "💖 A sᴛʀᴏɴɢ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ɪs ᴛʜᴇʀᴇ. Kᴇᴇᴘ ɴᴜʀᴛᴜʀɪɴɢ ɪᴛ.",
            "🪄 Yᴏᴜ'ᴠᴇ ɢᴏᴛ ᴀ ɢᴏᴏᴅ ᴄʜᴀɴᴄᴇ. Wᴏʀᴋ ᴏɴ ɪᴛ!",
            "🌸 Lᴏᴠᴇ ɪs ʙʟᴏssᴏᴍɪɴɢ, ᴋᴇᴇᴘ ɢᴏɪɴɢ!",
        ])
    else:
        return random.choice([
            "💞 Wᴏᴡ! A ᴍᴀᴛᴄʜ ᴍᴀᴅᴇ ɪɴ ʜᴇᴀᴠᴇɴ!",
            "💍 Pᴇʀғᴇᴄᴛ ᴍᴀᴛᴄʜ! Cʜᴇʀɪsʜ ᴛʜɪs ʙᴏɴᴅ.",
            "💘 Dᴇsᴛɪɴᴇᴅ ᴛᴏ ʙᴇ ᴛᴏɢᴇᴛʜᴇʀ. Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!",
        ])

@app.on_message(filters.command("love", prefixes=["/", "!"]))
async def love_command(_, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        return await message.reply_text("❌ Please provide **two names**.\n\n**Usage:** `/love Alice Bob`")

    name1 = args[1].strip()
    name2 = args[2].strip()

    if not name1 or not name2:
        return await message.reply_text("❌ Both names must be valid.")

    love_percentage = random.randint(10, 100)
    love_message = get_random_message(love_percentage)
    heart_bar = "❤️" * (love_percentage // 10) + "🤍" * ((100 - love_percentage) // 10)
    gif = random.choice(LOVE_GIFS)

    caption = f"""
💞 <b>ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ</b>

<b>{name1}</b> + <b>{name2}</b> = <b>{love_percentage}%</b>

{heart_bar}

{love_message}

<em>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></em>
""".strip()

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Try Again", switch_inline_query_current_chat="/love "),
                InlineKeyboardButton("💗 Share", switch_inline_query=f"/love {name1} {name2}")
            ]
        ]
    )

    try:
        await message.reply_animation(gif, caption=caption, reply_markup=buttons)
    except Exception:
        await message.reply_photo(gif, caption=caption, reply_markup=buttons)


__MODULE__ = "Lᴏᴠᴇ"
__HELP__ = """
**💘 ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ**

➤ `/love [name1] [name2]`  
ᴄᴀʟᴄᴜʟᴀᴛᴇ ᴛʜᴇ ʟᴏᴠᴇ ᴘᴇʀᴄᴇɴᴛᴀɢᴇ ʙᴇᴛᴡᴇᴇɴ ᴛᴡᴏ ɴᴀᴍᴇs 💑

__Eɴᴊᴏʏ ғᴜɴ ᴀɴᴅ sᴘʀᴇᴀᴅ ʟᴏᴠᴇ! 💕__

<b>💌 Message provided by</b> <a href="https://t.me/siyaprobot">Siya</a>
"""