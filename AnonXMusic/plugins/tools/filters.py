import re
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from AnonXMusic import app
from config import BOT_USERNAME
from AnonXMusic.utils.shadwo_ban import admin_filter
from AnonXMusic.utils.filtersdb import add_filter_db, get_filters_list, get_filter, stop_db, stop_all_db
from AnonXMusic.utils.filters_func import GetFIlterMessage, get_text_reason, SendFilterMessage
from AnonXMusic.utils.yumidb import user_admin

def validate_buttons(text):
    """Parse and validate multiple buttons from filter text."""
    buttons = []
    pattern = r"<button:(.*?)=(.*?)>"
    matches = re.findall(pattern, text)

    for name, url in matches:
        url = url.strip()
        if url.startswith(("http://", "https://", "tg://")):
            buttons.append(InlineKeyboardButton(text=name.strip(), url=url))
    
    # Remove the button markup from the message text
    clean_text = re.sub(pattern, "", text).strip()
    return clean_text, buttons

@app.on_message(filters.command("filter") & admin_filter)
@user_admin
async def _filter(client, message):
    chat_id = message.chat.id
    if message.reply_to_message and not len(message.command) == 2:
        return await message.reply("You need to give the filter a name!")

    filter_name, filter_reason = get_text_reason(message)
    if message.reply_to_message and not filter_reason:
        return await message.reply("You need to give the filter some content!")

    content, text, data_type = await GetFIlterMessage(message)
    await add_filter_db(chat_id, filter_name=filter_name, content=content, text=text, data_type=data_type)
    await message.reply(f"Saved filter `{filter_name}`.")

@app.on_message(~filters.bot & filters.group, group=4)
async def FilterCheckker(client, message):
    if not message.text:
        return
    text = message.text
    chat_id = message.chat.id
    if len(await get_filters_list(chat_id)) == 0:
        return

    ALL_FILTERS = await get_filters_list(chat_id)
    for filter_ in ALL_FILTERS:
        pattern = r"( |^|[^\w])" + re.escape(filter_) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            filter_name, content, text, data_type = await get_filter(chat_id, filter_)
            if text:
                clean_text, buttons = validate_buttons(text)
                markup = InlineKeyboardMarkup.from_button(buttons) if buttons else None
                await SendFilterMessage(
                    message=message,
                    filter_name=filter_,
                    content=content,
                    text=clean_text,
                    data_type=data_type,
                    reply_markup=markup,
                )
            else:
                await SendFilterMessage(
                    message=message,
                    filter_name=filter_,
                    content=content,
                    text=None,
                    data_type=data_type,
                    reply_markup=None,
                )
            return  # Stop after first match

@app.on_message(filters.command('filters') & filters.group)
async def _filters(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Group"
    FILTERS = await get_filters_list(chat_id)

    if not FILTERS:
        return await message.reply(f'No filters set in {chat_title}.')

    filters_list = f'List of filters in {chat_title}:\n'
    for filter_ in FILTERS:
        filters_list += f'- `{filter_}`\n'

    await message.reply(filters_list)

@app.on_message(filters.command('stopall') & admin_filter)
async def stopall(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title or "Group"
    user = await client.get_chat_member(chat_id, message.from_user.id)
    if user.status != ChatMemberStatus.OWNER:
        return await message.reply_text("Only the group owner can use this.")

    KEYBOARD = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='✅ Delete all filters', callback_data='custfilters_stopall')],
        [InlineKeyboardButton(text='❌ Cancel', callback_data='custfilters_cancel')]
    ])

    await message.reply(
        text=f'Are you sure you want to delete **all** filters in `{chat_title}`?',
        reply_markup=KEYBOARD
    )

@app.on_callback_query(filters.regex("^custfilters_"))
async def stopall_callback(client, cb: CallbackQuery):
    chat_id = cb.message.chat.id
    action = cb.data.split("_")[1]

    user = await client.get_chat_member(chat_id, cb.from_user.id)
    if user.status != ChatMemberStatus.OWNER:
        return await cb.answer("Only the group owner can do this!")

    if action == "stopall":
        await stop_all_db(chat_id)
        await cb.edit_message_text("✅ All filters have been deleted.")
    elif action == "cancel":
        await cb.edit_message_text("❌ Cancelled.")

@app.on_message(filters.command('stopfilter') & admin_filter)
@user_admin
async def stop_filter(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply('Usage: /stopfilter <filter name>')

    filter_name = message.command[1]
    if filter_name not in await get_filters_list(chat_id):
        return await message.reply("No such filter exists.")

    await stop_db(chat_id, filter_name)
    await message.reply(f"Stopped filter `{filter_name}`.")