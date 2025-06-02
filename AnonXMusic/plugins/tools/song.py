import os
import re
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaVideo,
    Message,
)
import yt_dlp

from AnonXMusic import app, YouTube
from config import BANNED_USERS, SONG_DOWNLOAD_DURATION, SONG_DOWNLOAD_DURATION_LIMIT
from ANNIEMUSIC.utils.decorators.language import language, languageCB
from AnonXMusic.utils.formatters import convert_bytes
from AnonXMusic.utils.inline.song import song_markup

cookies_file = "AnonXMusic/assets/cookies.txt"
SONG_COMMAND = ["song"]


@app.on_message(filters.command(SONG_COMMAND) & filters.group & ~BANNED_USERS)
@language
async def song_commad_group(client, message: Message, _):
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=_["SG_B_1"], url=f"https://t.me/{app.username}?start=song")]]
    )
    await message.reply_text(_["song_1"], reply_markup=buttons)


@app.on_message(filters.command(SONG_COMMAND) & filters.private & ~BANNED_USERS)
@language
async def song_commad_private(client, message: Message, _):
    await message.delete()
    url = await YouTube.url(message)
    mystic = await message.reply_text(_["play_1"])

    if url:
        if not await YouTube.exists(url):
            return await mystic.edit_text(_["song_5"])
        try:
            title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(url)
        except:
            return await mystic.edit_text(_["play_3"])

        if not duration_min or int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_4"].format(SONG_DOWNLOAD_DURATION, duration_min or "Unknown")
            )

        buttons = song_markup(_, vidid)
        await mystic.delete()
        return await message.reply_photo(
            thumbnail,
            caption=_["song_4"].format(title),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        if len(message.command) < 2:
            return await mystic.edit_text(_["song_2"])
        query = message.text.split(None, 1)[1]
        try:
            title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(query)
        except:
            return await mystic.edit_text(_["play_3"])

        if not duration_min or int(duration_sec) > SONG_DOWNLOAD_DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(SONG_DOWNLOAD_DURATION, duration_min or "Unknown")
            )

        buttons = song_markup(_, vidid)
        await mystic.delete()
        return await message.reply_photo(
            thumbnail,
            caption=_["song_4"].format(title),
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_callback_query(filters.regex("song_back") & ~BANNED_USERS)
@languageCB
async def songs_back_helper(client, CallbackQuery, _):
    _, data = CallbackQuery.data.split(None, 1)
    stype, vidid = data.split("|")
    buttons = song_markup(_, vidid)
    await CallbackQuery.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("song_helper") & ~BANNED_USERS)
@languageCB
async def song_helper_cb(client, CallbackQuery, _):
    _, data = CallbackQuery.data.split(None, 1)
    stype, vidid = data.split("|")

    try:
        await CallbackQuery.answer(_["song_6"], show_alert=True)
    except:
        pass

    try:
        formats_available, _ = await YouTube.formats(vidid, True)
    except:
        return await CallbackQuery.edit_message_text(_["song_7"])

    buttons = []
    added = set()

    if stype == "audio":
        for x in formats_available:
            if "audio" in x.get("format", "") and x.get("filesize"):
                form = x.get("format_note", "Unknown").title()
                if form in added:
                    continue
                added.add(form)
                sz = convert_bytes(x["filesize"])
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{form} Quality Audio = {sz}",
                            callback_data=f"song_download {stype}|{x['format_id']}|{vidid}",
                        )
                    ]
                )
    else:
        allowed = {160, 133, 134, 135, 136, 137, 298, 299, 264, 304, 266}
        for x in formats_available:
            if not x.get("filesize") or int(x["format_id"]) not in allowed:
                continue
            sz = convert_bytes(x["filesize"])
            label = x["format"].split("-")[-1].strip()
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{label} = {sz}",
                        callback_data=f"song_download {stype}|{x['format_id']}|{vidid}",
                    )
                ]
            )

    buttons.append(
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data=f"song_back {stype}|{vidid}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ]
    )

    await CallbackQuery.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("song_download") & ~BANNED_USERS)
@languageCB
async def song_download_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer("Downloading")
    except:
        pass

    _, data = CallbackQuery.data.split(None, 1)
    stype, format_id, vidid = data.split("|")
    mystic = await CallbackQuery.edit_message_text(_["song_8"])
    yturl = f"https://www.youtube.com/watch?v={vidid}"

    try:
        with yt_dlp.YoutubeDL({"quiet": True, "cookiefile": cookies_file}) as ytdl:
            info = ytdl.extract_info(yturl, download=False)
    except Exception as e:
        return await mystic.edit_text(_["song_9"].format(str(e)))

    title = re.sub(r"\W+", " ", info["title"]).strip()
    duration = info.get("duration", 0)
    thumb = await CallbackQuery.message.download()

    try:
        file_path = await YouTube.download(
            yturl,
            mystic,
            songvideo=(stype == "video"),
            songaudio=(stype == "audio"),
            format_id=format_id,
            title=title,
        )
    except Exception as e:
        return await mystic.edit_text(_["song_9"].format(str(e)))

    await mystic.edit_text(_["song_11"])
    await app.send_chat_action(
        chat_id=CallbackQuery.message.chat.id,
        action=ChatAction.UPLOAD_VIDEO if stype == "video" else ChatAction.UPLOAD_AUDIO,
    )

    try:
        if stype == "video":
            media = InputMediaVideo(
                media=file_path,
                caption=title,
                duration=duration,
                thumb=thumb,
                width=CallbackQuery.message.photo.width,
                height=CallbackQuery.message.photo.height,
                supports_streaming=True,
            )
        else:
            media = InputMediaAudio(
                media=file_path,
                caption=title,
                duration=duration,
                thumb=thumb,
                title=title,
                performer=info.get("uploader", "Unknown"),
            )
        await CallbackQuery.edit_message_media(media=media)
    except Exception as e:
        print(e)
        return await mystic.edit_text(_["song_10"])

    os.remove(file_path)