import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from AnonXMusic import app
from AnonXMusic.misc import _boot_
from AnonXMusic.plugins.sudo.sudoers import sudoers_list
from AnonXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AnonXMusic.utils.decorators.language import LanguageStart
from AnonXMusic.utils.formatters import get_readable_time
from AnonXMusic.utils.inline import help_pannel, private_panel, start_panel

START_MEDIA = "https://files.catbox.moe/kooj9d.mp4"

START_CAPTION = """
<a href="{media}">&#8205;</a>
<b>✿ 𝒀𝒐𝒌𝒐𝒔𝒐, {mention}~ (≧◡≦)</b>
ɪ'ᴍ <b>{bot}</b>, ʏᴏᴜʀ ᴋᴀᴡᴀɪɪ ᴍᴜsɪᴄ ʙᴏᴛ ♫  
⤷ ʟɪᴠᴇ sᴛʀᴇᴀᴍs + ᴘʟᴀʏʟɪsᴛ  
⤷ ᴀɴɪᴍᴇ ғᴇᴇʟs ✧ ᴄᴏᴍᴍᴀɴᴅs → <code>/help</code>

<b>⸙ ᴅᴇᴠ :</b> <a href="https://t.me/I_shadwoo">sʜᴀ</a> 〜(꒪꒳꒪)〜
"""


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_video(
                video=START_MEDIA,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ ᴄʜᴇᴄᴋᴇᴅ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username}",
                )
            return

        elif name.startswith("inf"):
            m = await message.reply_text("🔍")
            query = name.replace("info_", "", 1)
            link = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(text=_["S_B_8"], url=link),
                    InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                ]]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴄʜᴇᴄᴋᴇᴅ ᴀ sᴏɴɢ ɪɴғᴏ.\n<b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username}",
                )

    out = InlineKeyboardMarkup(private_panel(_))
    caption = START_CAPTION.format(
        mention=message.from_user.mention,
        bot=app.mention,
        media=START_MEDIA,
    )
    await message.reply_text(caption, reply_markup=out)

    if await is_on_off(2):
        return await app.send_message(
            chat_id=config.LOGGER_ID,
            text=f"{message.from_user.mention} sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n<b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username}",
        )


@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(_, message: Message, _):
    out = InlineKeyboardMarkup(start_panel(_))
    uptime = int(time.time() - _boot_)
    text = _["start_1"].format(app.mention, get_readable_time(uptime))
    await message.reply_text(text, reply_markup=out)
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = InlineKeyboardMarkup(start_panel(_))
                await message.reply_video(
                    video=START_MEDIA,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=out,
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as e:
            print(f"Error in welcome: {e}")