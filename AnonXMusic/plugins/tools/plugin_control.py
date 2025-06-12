from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from AnonXMusic import app
from config import OWNER_ID
from AnonXMusic.utils.plugin_manager import (
    list_plugins, load_plugin, unload_plugin,
    loaded_plugins, disabled_plugins
)
import time


@app.on_message(filters.command("pluginlist") & filters.user(OWNER_ID))
async def plugin_list(_, message: Message):
    plugins = list_plugins()
    if not plugins:
        return await message.reply_text("❌ No plugins found.")

    rows = []
    for name in plugins:
        status = "✅" if name not in disabled_plugins else "🚫"
        uptime = ""
        if name in loaded_plugins:
            delta = int(time.time() - loaded_plugins[name])
            uptime = f" ({delta}s)"
        btn_text = f"{status} {name}{uptime}"
        callback_data = f"toggle_plugin:{name}"
        rows.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])

    await message.reply_text(
        "🧩 <b>Plugin Manager</b>\nTap to Enable/Disable plugins:",
        reply_markup=InlineKeyboardMarkup(rows),
    )


@app.on_callback_query(filters.regex(r"toggle_plugin:(.+)"))
async def toggle_plugin(_, query: CallbackQuery):
    plugin = query.data.split(":")[1]
    if plugin in disabled_plugins:
        result = load_plugin(plugin)
        if result is True:
            text = f"✅ <b>{plugin}</b> re-enabled successfully."
        else:
            text = f"❌ Failed to enable <b>{plugin}</b>:\n<code>{result}</code>"
    else:
        result = unload_plugin(plugin)
        if result:
            text = f"🚫 <b>{plugin}</b> has been disabled."
        else:
            text = f"❌ Failed to disable <b>{plugin}</b>."

    await query.answer("Plugin toggled", show_alert=False)
    return await plugin_list(_, query.message)