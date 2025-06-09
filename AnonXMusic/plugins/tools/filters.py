import re
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from AnonXMusic import app
from config import BOT_USERNAME
from AnonXMusic.utils.autofix import auto_fix_handler  # ✅ Auto error handler
from AnonXMusic.utils.shadwo_ban import admin_filter
from AnonXMusic.utils.filtersdb import (
    add_filter_db,
    get_filters_list,
    get_filter,
    stop_db,
    stop_all_db,
)
from AnonXMusic.utils.filters_func import GetFIlterMessage, get_text_reason, SendFilterMessage
from AnonXMusic.utils.yumidb import user_admin


@app.on_message(filters.command("filter") & admin_filter)
@user_admin
@auto_fix_handler
async def _filter(client, message):
    chat_id = message.chat.id

    if message.reply_to_message and not len(message.command) == 2:
        await message.reply("You need to give the filter a name!", parse_mode=ParseMode.HTML)
        return

    filter_name, filter_reason = get_text_reason(message)

    if message.reply_to_message and not len(message.command) >= 2:
        await message.reply("You need to give the filter some content!", parse_mode=ParseMode.HTML)
        return

    content, text, data_type = await GetFIlterMessage(message)
    await add_filter_db(chat_id, filter_name=filter_name, content=content, text=text, data_type=data_type)
    await message.reply(
        f"Saved filter '<b>{filter_name}</b>'.",
        parse_mode=ParseMode.HTML
    )


@app.on_message(~filters.bot & filters.group, group=4)
@auto_fix_handler
async def FilterCheckker(client, message):
    if not message.text:
        return

    text = message.text
    chat_id = message.chat.id

    ALL_FILTERS = await get_filters_list(chat_id)
    if not ALL_FILTERS:
        return

    for filter_ in ALL_FILTERS:
        if (
            message.command
            and message.command[0] == 'filter'
            and len(message.command) >= 2
            and message.command[1] == filter_
        ):
            return

        pattern = r"( |^|[^\w])" + re.escape(filter_) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            filter_name, content, text, data_type = await get_filter(chat_id, filter_)
            await SendFilterMessage(
                message=message,
                filter_name=filter_,
                content=content,
                text=text,
                data_type=data_type
            )
            return


@app.on_message(filters.command('filters') & filters.group)
@auto_fix_handler
async def _filters(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "local"

    FILTERS = await get_filters_list(chat_id)
    if not FILTERS:
        await message.reply(
            f'No filters in <b>{chat_title}</b>.',
            parse_mode=ParseMode.HTML
        )
        return

    filters_list = f'<b>List of filters in {chat_title}:</b>\n'
    for filter_ in FILTERS:
        filters_list += f'• <code>{filter_}</code>\n'

    await message.reply(
        filters_list,
        parse_mode=ParseMode.HTML
    )


@app.on_message(filters.command('stopall') & admin_filter)
@auto_fix_handler
async def stopall(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Group"
    user = await client.get_chat_member(chat_id, message.from_user.id)

    if user.status != ChatMemberStatus.OWNER:
        return await message.reply_text("Only the group owner can use this!", parse_mode=ParseMode.HTML)

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
@auto_fix_handler
async def stopall_callback(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    query_data = callback_query.data.split('_')[1]
    user = await client.get_chat_member(chat_id, callback_query.from_user.id)

    if user.status != ChatMemberStatus.OWNER:
        return await callback_query.answer("Only the group owner can do this!", show_alert=True)

    if query_data == 'stopall':
        await stop_all_db(chat_id)
        await callback_query.edit_message_text("All filters have been deleted.", parse_mode=ParseMode.HTML)
    elif query_data == 'cancel':
        await callback_query.edit_message_text("Cancelled.", parse_mode=ParseMode.HTML)


@app.on_message(filters.command('stopfilter') & admin_filter)
@user_admin
@auto_fix_handler
async def stop(client, message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        await message.reply('Use /stopfilter <filter name>', parse_mode=ParseMode.HTML)
        return

    filter_name = message.command[1]
    if filter_name not in await get_filters_list(chat_id):
        await message.reply("There’s no filter saved with that name!", parse_mode=ParseMode.HTML)
        return

    await stop_db(chat_id, filter_name)
    await message.reply(
        f"Deleted filter '<b>{filter_name}</b>'.",
        parse_mode=ParseMode.HTML
    )