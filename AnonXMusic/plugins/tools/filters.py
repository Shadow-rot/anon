import re
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from AnonXMusic import app
from config import BOT_USERNAME
from AnonXMusic.utils.shadwo_ban import admin_filter
from AnonXMusic.utils.filtersdb import *
from AnonXMusic.utils.filters_func import GetFIlterMessage, get_text_reason, SendFilterMessage
from AnonXMusic.utils.yumidb import user_admin


@app.on_message(filters.command("filter") & admin_filter)
@user_admin
async def _filter(client, message: Message):
    chat_id = message.chat.id

    if message.reply_to_message and len(message.command) < 2:
        return await message.reply("You need to give the filter a name!")

    filter_name, filter_reason = get_text_reason(message)

    content, text, data_type = await GetFIlterMessage(message)
    if not text and not content:
        return await message.reply("You need to provide filter content!")

    await add_filter_db(chat_id, filter_name=filter_name, content=content, text=text, data_type=data_type)
    await message.reply(
        f"Saved filter '<b>{filter_name}</b>'.",
        parse_mode=ParseMode.HTML
    )


@app.on_message(~filters.bot & filters.group, group=4)
async def FilterChecker(client, message: Message):
    if not message.text:
        return

    chat_id = message.chat.id
    ALL_FILTERS = await get_filters_list(chat_id)
    if not ALL_FILTERS:
        return

    text = message.text.lower()

    for filter_ in ALL_FILTERS:
        # Avoid recursion if someone types "/filter something"
        if message.text.startswith("/filter") and filter_ in message.text:
            return

        # Case-insensitive match with word boundaries
        pattern = r"( |^|[^\w])" + re.escape(filter_.lower()) + r"( |$|[^\w])"
        if re.search(pattern, text):
            _, content, ftext, dtype = await get_filter(chat_id, filter_)
            await SendFilterMessage(message, filter_, content, ftext, dtype)
            return


@app.on_message(filters.command('filters') & filters.group)
async def _filters(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Group"

    FILTERS = await get_filters_list(chat_id)
    if not FILTERS:
        return await message.reply(f"No filters in <b>{chat_title}</b>.", parse_mode=ParseMode.HTML)

    text = f"<b>List of filters in {chat_title}:</b>\n"
    for filter_ in FILTERS:
        text += f"• <code>{filter_}</code>\n"

    await message.reply(text, parse_mode=ParseMode.HTML)


@app.on_message(filters.command('stopfilter') & admin_filter)
@user_admin
async def stop_filter(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply("Usage: /stopfilter <filter name>")

    filter_name = message.command[1]
    FILTERS = await get_filters_list(chat_id)
    if filter_name not in FILTERS:
        return await message.reply("There's no filter saved with that name!")

    await stop_db(chat_id, filter_name)
    await message.reply(f"Deleted filter '<b>{filter_name}</b>'.", parse_mode=ParseMode.HTML)


@app.on_message(filters.command('stopall') & admin_filter)
async def stopall(client, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Group"
    user = await client.get_chat_member(chat_id, message.from_user.id)

    if user.status != ChatMemberStatus.OWNER:
        return await message.reply("Only the group owner can use this!")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Delete all filters", callback_data="custfilters_stopall")],
        [InlineKeyboardButton("Cancel", callback_data="custfilters_cancel")]
    ])

    await message.reply(
        f"Are you sure you want to delete all filters in <b>{chat_title}</b>?\nThis action is irreversible.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


@app.on_callback_query(filters.regex("^custfilters_"))
async def stopall_callback(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    action = callback_query.data.split('_')[1]

    user = await client.get_chat_member(chat_id, callback_query.from_user.id)
    if user.status != ChatMemberStatus.OWNER:
        return await callback_query.answer("Only the group owner can do this!")

    if action == "stopall":
        await stop_all_db(chat_id)
        await callback_query.edit_message_text("All filters have been deleted.")
    elif action == "cancel":
        await callback_query.edit_message_text("Cancelled.")