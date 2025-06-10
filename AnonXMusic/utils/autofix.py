import asyncio
import traceback
from collections import defaultdict
from inspect import iscoroutinefunction

from pyrogram.errors import (
    ButtonUrlInvalid,
    MediaEmpty,
    WebpageCurlFailed,
    RPCError,
    FloodWait,
    MessageNotModified,
    MessageIdInvalid,
    BadRequest,
    ChatWriteForbidden,
    MessageDeleteForbidden,
    MessageEditTimeExpired,
)
from pyrogram.enums import ParseMode
from AnonXMusic import app
from config import OWNER_ID

crash_counter = defaultdict(int)

def auto_fix_handler(func):
    async def wrapper(client, *args, **kwargs):
        retries = 3

        while retries > 0:
            try:
                # ✅ Check if func is a coroutine (async)
                if iscoroutinefunction(func):
                    await func(client, *args, **kwargs)
                else:
                    func(client, *args, **kwargs)  # call sync function
                return
            except FloodWait as e:
                print(f"[FloodWait] Sleeping for {e.x} seconds before retrying {func.__name__}")
                await asyncio.sleep(e.x)
                retries -= 1

            except (
                ButtonUrlInvalid,
                MediaEmpty,
                WebpageCurlFailed,
                RPCError,
                BadRequest,
                ChatWriteForbidden,
                MessageDeleteForbidden,
                MessageEditTimeExpired,
                MessageNotModified,
                MessageIdInvalid,
            ) as e:
                message_obj = _find_message_or_callback(args, kwargs)
                if message_obj:
                    try:
                        await message_obj.reply(
                            f"⚠️ Minor Telegram API error:\n<code>{e}</code>",
                            parse_mode=ParseMode.HTML,
                            quote=True,
                        )
                    except Exception:
                        pass
                else:
                    print(f"[MINOR ERROR] {func.__name__} failed with: {e}")
                return

            except Exception as e:
                crash_counter[func.__name__] += 1
                tb = traceback.format_exc()
                print(f"[ERROR] Exception in {func.__name__}:\n{tb}")

                try:
                    await client.send_message(
                        OWNER_ID,
                        f"❗️ <b>Exception in handler:</b> <code>{func.__name__}</code>\n"
                        f"<pre>{tb}</pre>",
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )

                    if crash_counter[func.__name__] >= 5:
                        await client.send_message(
                            OWNER_ID,
                            f"🚨 <b>{func.__name__}</b> has crashed <code>{crash_counter[func.__name__]}</code> times.",
                            parse_mode=ParseMode.HTML,
                        )

                except Exception as notify_err:
                    print(f"[ERROR] Failed to notify owner: {notify_err}")

                message_obj = _find_message_or_callback(args, kwargs)
                if message_obj:
                    try:
                        await message_obj.reply(
                            "❌ An unexpected error occurred. The bot owner has been notified.",
                            quote=True,
                        )
                    except Exception:
                        pass
                return

    def _find_message_or_callback(args, kwargs):
        for arg in args:
            if hasattr(arg, "reply") or hasattr(arg, "answer"):
                return arg
        return kwargs.get("callback_query")

    return wrapper