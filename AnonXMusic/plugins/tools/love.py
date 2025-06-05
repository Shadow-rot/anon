import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

LOVE_MEDIA = [
    "https://te.legra.ph/file/4ec5ae4381dffb039b4ef.jpg",
    "https://files.catbox.moe/853x8v.jpg",
    "https://files.catbox.moe/c9l8ze.jpg",
    "https://files.catbox.moe/r6dwqd.jpg",
    "https://files.catbox.moe/dodb0z.jpg",
]

def get_random_message(love_percentage: int) -> str:
    if love_percentage <= 30:
        return random.choice([
            "💔 Nᴏᴛ ᴍᴜᴄʜ sᴘᴀʀᴋ ʏᴇᴛ... Bᴜᴛ ʟᴏᴠᴇ ᴛᴀᴋᴇs ᴛɪᴍᴇ!",
            "😅 Jᴜsᴛ ғʀɪᴇɴᴅs... ғᴏʀ ɴᴏᴡ.",
            "🌧 A ʙɪᴛ ᴄʟᴏᴜᴅʏ, ʙᴜᴛ ᴛʜᴇ sᴜɴ ᴍɪɢʜᴛ sʜɪɴᴇ.",
        ])
    elif love_percentage <= 70:
        return random.choice([
            "🌼 Sᴏᴍᴇᴛʜɪɴɢ ʙᴇᴀᴜᴛɪғᴜʟ ɪs ɢʀᴏᴡɪɴɢ!",
            "💖 A ᴘʀᴏᴍɪsɪɴɢ ᴍᴀᴛᴄʜ. Kᴇᴇᴘ ɢᴏɪɴɢ!",
            "🫶 Cᴏɴɴᴇᴄᴛɪᴏɴ ᴅᴇᴛᴇᴄᴛᴇᴅ — ɪɴᴠᴇsᴛ ᴛɪᴍᴇ 💕",
        ])
    else:
        return random.choice([
            "💘 Sᴏᴜʟᴍᴀᴛᴇs ᴀʟᴇʀᴛ!",
            "💍 Rɪɴɢs ɪɴ ʏᴏᴜʀ ғᴜᴛᴜʀᴇ?",
            "🔥 Tʜɪs ɪs ᴏɴ ғɪʀᴇ! A ᴛʀᴜᴇ ᴍᴀᴛᴄʜ!",
        ])

@app.on_message(filters.command("ar", prefixes=["/", "!"]))
async def love_command(_, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        return await message.reply_text(
            "❌ <b>Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴡᴏ ɴᴀᴍᴇs.</b>\n\n<u>Usage:</u> <code>/love Alice Bob</code>"
        )

    name1 = args[1].strip()
    name2 = args[2].strip()

    if not name1 or not name2:
        return await message.reply_text("❌ <b>Bᴏᴛʜ ɴᴀᴍᴇs ᴍᴜsᴛ ʙᴇ ᴠᴀʟɪᴅ.</b>")

    love_percentage = random.randint(10, 100)
    love_message = get_random_message(love_percentage)
    
    hearts = "❤️‍🔥" * (love_percentage // 20)
    extras = "💌✨💞"
    bar = f"{hearts}{random.choice(extras)}"

    media = random.choice(LOVE_MEDIA)

    caption = f"""<b>💘 ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛɪᴏɴ</b>
<b>{name1}</b> + <b>{name2}</b> = <b>{love_percentage}%</b>
{bar}
{love_message}
<a href="{media}">&#8205;</a>
<em>Message provided by <a href='https://t.me/siyaprobot'>Siya</a></em>""".strip()

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Try Again", switch_inline_query_current_chat="/love "),
            InlineKeyboardButton("💗 Share", switch_inline_query=f"/love {name1} {name2}")
        ]
    ])

    await message.reply_text(caption, reply_markup=buttons)

MODULE = "Lᴏᴠᴇ"
HELP = """
<b>💘 ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ</b>

➤ <code>/love [name1] [name2]</code>  
ᴄᴀʟᴄᴜʟᴀᴛᴇ ʟᴏᴠᴇ ᴘᴇʀᴄᴇɴᴛᴀɢᴇ ʙᴇᴛᴡᴇᴇɴ ᴛᴡᴏ ɴᴀᴍᴇs 💑

<b>💌 Message provided by</b> <a href="https://t.me/siyaprobot">Siya</a>
"""