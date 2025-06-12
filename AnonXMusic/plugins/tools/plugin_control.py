import sys
import time
import importlib
from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app
from config import OWNER_ID
from AnonXMusic.plugins import ALL_MODULES

# Track plugin states
loaded_plugins = {name: time.time() for name in ALL_MODULES}
disabled_plugins = set()
failed_plugins = {}

# Allow these prefixes
OWNER_COMMAND = filters.command(
    ["plist", "ep", "dp", "rp", "pi"], prefixes=["/", ".", "!", "?", "+", "-", ",", ">"]
) & filters.user(OWNER_ID)

# Helpers
def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02}"

def load_plugin(name):
    try:
        if name in sys.modules:
            importlib.reload(sys.modules[f"AnonXMusic.plugins.{name}"])
        else:
            importlib.import_module(f"AnonXMusic.plugins.{name}")
        loaded_plugins[name] = time.time()
        disabled_plugins.discard(name)
        failed_plugins.pop(name, None)
        return True
    except Exception as e:
        failed_plugins[name] = str(e)
        return str(e)

def unload_plugin(name):
    module = f"AnonXMusic.plugins.{name}"
    if module in sys.modules:
        del sys.modules[module]
    if name in ALL_MODULES or name in loaded_plugins:
        disabled_plugins.add(name)
        return True
    return False


@app.on_message(filters.command("plist", prefixes=["/", ".", "!", "?", "+", "-", ",", ">"]) & filters.user(OWNER_ID))
async def plugin_list_cmd(_, message: Message):
    all_plugins = sorted(set(ALL_MODULES + list(disabled_plugins)))
    if not all_plugins:
        return await message.reply("❌ No plugins found.")

    lines = ["<b>🧩 Plugin Overview:</b>"]
    for name in all_plugins:
        if name in failed_plugins:
            status = "⚠️ Error"
        elif name in disabled_plugins:
            status = "🚫 Disabled"
        else:
            status = "✅ Enabled"
        uptime = ""
        if name in loaded_plugins:
            uptime = f" — <i>{format_seconds(int(time.time() - loaded_plugins[name]))}</i>"
        lines.append(f"• <code>{name}</code>: {status}{uptime}")

    await message.reply_text("\n".join(lines))


@app.on_message(filters.command("ep", prefixes=["/", ".", "!", "?", "+", "-", ",", ">"]) & filters.user(OWNER_ID))
async def enable_plugin_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: <code>/ep plugin_name</code>")
    name = message.command[1].strip()
    if name not in ALL_MODULES and name not in disabled_plugins:
        return await message.reply("❌ Invalid plugin name.")

    result = load_plugin(name)
    if result is True:
        await message.reply(f"✅ <code>{name}</code> enabled successfully.")
    else:
        await message.reply(f"❌ Failed to enable <code>{name}</code>:\n<code>{result}</code>")


@app.on_message(filters.command("dp", prefixes=["/", ".", "!", "?", "+", "-", ",", ">"]) & filters.user(OWNER_ID))
async def disable_plugin_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: <code>/dp plugin_name</code>")
    name = message.command[1].strip()
    if name not in ALL_MODULES:
        return await message.reply("❌ Invalid plugin name.")

    result = unload_plugin(name)
    if result:
        await message.reply(f"🚫 <code>{name}</code> disabled successfully.")
    else:
        await message.reply("❌ Failed to disable the plugin.")


@app.on_message(filters.command("rp", prefixes=["/", ".", "!", "?", "+", "-", ",", ">"]) & filters.user(OWNER_ID))
async def reload_plugin_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: <code>/rp plugin_name</code>")
    name = message.command[1].strip()
    if name not in ALL_MODULES and name not in disabled_plugins:
        return await message.reply("❌ Invalid plugin name.")

    unload_plugin(name)
    result = load_plugin(name)
    if result is True:
        await message.reply(f"🔁 <code>{name}</code> reloaded successfully.")
    else:
        await message.reply(f"❌ Reload failed for <code>{name}</code>:\n<code>{result}</code>")


@app.on_message(filters.command("pi", prefixes=["/", ".", "!", "?", "+", "-", ",", ">"]) & filters.user(OWNER_ID))
async def plugin_info_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: <code>/pi plugin_name</code>")
    name = message.command[1].strip()

    if name not in ALL_MODULES and name not in disabled_plugins and name not in failed_plugins:
        return await message.reply("❌ Plugin not recognized.")

    status = (
        "✅ Enabled" if name not in disabled_plugins
        else "🚫 Disabled" if name not in failed_plugins
        else "⚠️ Error"
    )
    uptime = (
        f"<i>{format_seconds(int(time.time() - loaded_plugins[name]))}</i> uptime"
        if name in loaded_plugins else "N/A"
    )
    error = failed_plugins.get(name)

    text = f"<b>📦 Plugin:</b> <code>{name}</code>\n"
    text += f"<b>Status:</b> {status}\n"
    text += f"<b>Uptime:</b> {uptime}\n"
    if error:
        text += f"<b>Error:</b>\n<code>{error}</code>"

    await message.reply_text(text)