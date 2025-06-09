"""
import asyncio
import logging
from datetime import datetime, timedelta
from pyrogram.types import Message
from pyrogram import Client, filters
from config import OWNER_ID

# Plugin crash log: {plugin_name: [timestamp, ...]}
PLUGIN_ERRORS = {}
# Disabled plugins: {plugin_name: True}
DISABLED_PLUGINS = {}

CRASH_LIMIT = 3
CRASH_WINDOW = timedelta(minutes=10)

def guard(plugin_name):
    def decorator(func):
        async def wrapper(client: Client, message: Message):
            if DISABLED_PLUGINS.get(plugin_name, False):
                return  # plugin is currently disabled
            try:
                await func(client, message)
            except Exception as e:
                now = datetime.utcnow()
                PLUGIN_ERRORS.setdefault(plugin_name, []).append(now)
                PLUGIN_ERRORS[plugin_name] = [
                    t for t in PLUGIN_ERRORS[plugin_name] if now - t < CRASH_WINDOW
                ]
                if len(PLUGIN_ERRORS[plugin_name]) >= CRASH_LIMIT:
                    DISABLED_PLUGINS[plugin_name] = True
                    try:
                        await client.send_message(
                            OWNER_ID,
                            f"🚫 Plugin `{plugin_name}` crashed {CRASH_LIMIT} times in 10 minutes.\nIt has been auto-disabled.\nUse `/retryfix {plugin_name}` to re-enable it.",
                        )
                    except:
                        pass
                logging.exception(f"[AutoFixGuard] Plugin '{plugin_name}' crashed:")
        return wrapper
    return decorator

# Manual recovery command
def add_retryfix_command(app: Client):
    @app.on_message(filters.command("retryfix") & filters.user(OWNER_ID))
    async def retryfix(_, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("Usage: `/retryfix plugin_name`")
        plugin = message.command[1]
        if DISABLED_PLUGINS.pop(plugin, None):
            PLUGIN_ERRORS.pop(plugin, None)
            return await message.reply_text(f"✅ Plugin `{plugin}` has been re-enabled.")
        else:
            return await message.reply_text(f"⚠️ Plugin `{plugin}` is not disabled.")
"""