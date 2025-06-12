from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from AnonXMusic import app
from config import OWNER_ID
from AnonXMusic.plugins import ALL_MODULES
import importlib
import sys
import time

# Track plugin state
loaded_plugins = {name: time.time() for name in ALL_MODULES}
disabled_plugins = set()

# Load plugin dynamically
def load_plugin(name):
    try:
        if name in sys.modules:
            importlib.reload(sys.modules[f"AnonXMusic.plugins.{name}"])
        else:
            importlib.import_module(f"AnonXMusic.plugins.{name}")
        loaded_plugins[name] = time.time()
        disabled_plugins.discard(name)
        return True
    except Exception as e:
        return str(e)

# Unload plugin
def unload_plugin(name):
    module = f"AnonXMusic.plugins.{name}"
    if module in sys.modules:
        del sys.modules[module]
        disabled_plugins.add(name)
        return True
    return False

# Plugin List with Buttons
@app.on_message(filters.command("pluginlist") & filters.user(OWNER_ID))
async def plugin_list(_, message: Message):
    plugins = sorted(set(ALL_MODULES + list(disabled_plugins)))
    buttons = []
    for name in plugins:
        status = "✅" if name not in disabled_plugins else "🚫"
        uptime = ""
        if name in loaded_plugins:
            delta = int(time.time() - loaded_plugins[name])
            uptime = f" ({delta}s)"
        buttons.append([
            InlineKeyboardButton(
                f"{status} {name}{uptime}",
                callback_data=f"toggle_plugin:{name}"
            )
        ])

    await message.reply_text(
        "🧩 <b>Plugin Manager</b>\nTap to Enable/Disable plugins:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Toggle Plugin from Callback
@app.on_callback_query(filters.regex(r"toggle_plugin:(.+)"))
async def toggle_plugin(_, query: CallbackQuery):
    plugin = query.matches[0].group(1)

    if plugin in disabled_plugins:
        result = load_plugin(plugin)
        msg = f"✅ <b>{plugin}</b> re-enabled." if result is True else f"❌ Failed:\n<code>{result}</code>"
    else:
        result = unload_plugin(plugin)
        msg = f"🚫 <b>{plugin}</b> disabled." if result else f"❌ Failed to disable <b>{plugin}</b>"

    await query.answer("Toggled", show_alert=False)
    await plugin_list(_, query.message)