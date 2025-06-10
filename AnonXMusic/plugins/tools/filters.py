import re
from AnonXMusic import app
from config import BOT_USERNAME
from AnonXMusic.utils.shadwo_ban import admin_filter
from AnonXMusic.utils.filtersdb import *
from AnonXMusic.utils.filters_func import GetFIlterMessage, get_text_reason, SendFilterMessage
from AnonXMusic.utils.yumidb import user_admin
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# /filter command
@app.on_message(filters.command("filter") & admin_filter)
@user_admin
async def _filter(client, message):
    chat_id = message.chat.id

    if not message.command or len(message.command) < 2:
        await message.reply("You need to give the filter a name!", parse_mode=ParseMode.HTML)
        return

    if message.reply_to_message is None:
        await message.reply("You need to reply to a message with filter content!", parse_mode=ParseMode.HTML)
        return

    if not (message.reply_to_message.text or message.reply_to_message.caption or message.reply_to_message.media):
        await message.reply("You need to give the filter some content!", parse_mode=ParseMode.HTML)
        return

    filter_name, filter_reason = get_text_reason(message)
    content, text, data_type = await GetFIlterMessage(message)

    await add_filter_db(chat_id, filter_name=filter_name, content=content, text=text, data_type=data_type)

    await message.reply(
        f"Saved filter '<b>{filter_name}</b>'.", parse_mode=ParseMode.HTML
    )

# Filter trigger listener
@app.on_message(~filters.bot & filters.group, group=4)
async def FilterCheckker(client, message):
    if not message.text:
        return

    text = message.text
    chat_id = message.chat.id

    ALL_FILTERS = await get_filters_list(chat_id)
    if not ALL_FILTERS:
        return

    for filter_ in ALL_FILTERS:
        if not filter_:
            continue

        if message.command and len(message.command) >= 2 and message.command[0] == 'filter' and message.command[1] == filter_:
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

# /filters command
@app.on_message(filters.command('filters') & filters.group)
async def _filters(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "this chat"

    FILTERS = await get_filters_list(chat_id)

    if not FILTERS:
        await message.reply(f'No filters in {chat_title}.', parse_mode=ParseMode.HTML)
        return

    filters_list = f'<b>List of filters in {chat_title}:</b>\n'
    for filter_ in FILTERS:
        filters_list += f'• <code>{filter_}</code>\n'

    await message.reply(filters_list, parse_mode=ParseMode.HTML)

# /stopall confirmation
@app.on_message(filters.command('stopall') & admin_filter)
async def stopall(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "this chat"

    user = await client.get_chat_member(chat_id, message.from_user.id)
    if user.status != ChatMemberStatus.OWNER:
        return await message.reply("Only the group owner can use this!", parse_mode=ParseMode.HTML)

    KEYBOARD = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Delete all filters', callback_data='custfilters_stopall')],
        [InlineKeyboardButton(text='Cancel', callback_data='custfilters_cancel')]
    ])

    await message.reply(
        text=(f'Are you sure you want to stop <b>ALL</b> filters in {chat_title}? This action is irreversible.'),
        reply_markup=KEYBOARD,
        parse_mode=ParseMode.HTML
    )

# stopall button callback
@app.on_callback_query(filters.regex("^custfilters_"))
async def stopall_callback(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    query_data = callback_query.data.split('_')[1]

    user = await client.get_chat_member(chat_id, callback_query.from_user.id)
    if user.status != ChatMemberStatus.OWNER:
        return await callback_query.answer("Only the group owner can do this!", show_alert=True)

    if query_data == 'stopall':
        await stop_all_db(chat_id)
        await callback_query.edit_message_text("I've deleted all chat filters.", parse_mode=ParseMode.HTML)

    elif query_data == 'cancel':
        await callback_query.edit_message_text("Cancelled.", parse_mode=ParseMode.HTML)

# /stopfilter command
@app.on_message(filters.command('stopfilter') & admin_filter)
@user_admin
async def stop(client, message):
    chat_id = message.chat.id

    if not message.command or len(message.command) < 2:
        await message.reply('Usage: /stopfilter <filter_name>', parse_mode=ParseMode.HTML)
        return

    filter_name = message.command[1]
    if filter_name not in await get_filters_list(chat_id):
        await message.reply("You haven't saved any filters with this word yet!", parse_mode=ParseMode.HTML)
        return

    await stop_db(chat_id, filter_name)
    await message.reply(f"I've stopped <b>{filter_name}</b>.", parse_mode=ParseMode.HTML)