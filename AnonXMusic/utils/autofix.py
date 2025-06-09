"""
import asyncio
import traceback
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
from config import OWNER_ID  # Make sure you have OWNER_ID in your config


def auto_fix_handler(func):
    async def wrapper(client, *args, **kwargs):
        try:
            await func(client, *args, **kwargs)

        except FloodWait as e:
            print(f"[FloodWait] Sleeping for {e.x} seconds before retrying {func.__name__}")
            await asyncio.sleep(e.x)
            await func(client, *args, **kwargs)

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
            # Known minor errors - notify user if possible
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

        except Exception as e:
            # Unexpected error — log full traceback & notify owner privately
            tb = traceback.format_exc()
            print(f"[ERROR] Exception in {func.__name__}:\n{tb}")

            # Notify bot owner privately with error details
            try:
                await client.send_message(
                    OWNER_ID,
                    f"❗️ <b>Exception in handler:</b> <code>{func.__name__}</code>\n"
                    f"<pre>{tb}</pre>",
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as notify_err:
                print(f"[ERROR] Failed to notify owner: {notify_err}")

            # Optionally notify user if possible
            message_obj = _find_message_or_callback(args, kwargs)
            if message_obj:
                try:
                    await message_obj.reply(
                        "❌ An unexpected error occurred. The bot owner has been notified.",
                        quote=True,
                    )
                except Exception:
                    pass  # fail silently

    def _find_message_or_callback(args, kwargs):
        # Try to find message-like or callback query-like object for reply/answer
        for arg in args:
            if hasattr(arg, "reply") or hasattr(arg, "answer"):
                return arg
        if "callback_query" in kwargs:
            return kwargs["callback_query"]
        return None

    return wrapper
"""