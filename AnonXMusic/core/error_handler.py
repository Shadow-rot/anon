import logging
import traceback
import asyncio
import datetime
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from config import OWNER_ID


class TelegramErrorHandler(logging.Handler):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            asyncio.create_task(self.send_error(record))

    async def send_error(self, record):
        try:
            # Traceback string
            tb = ''.join(traceback.format_exception(
                record.exc_info[0], record.exc_info[1], record.exc_info[2]
            )) if record.exc_info else "No traceback available."

            # Timestamp, file, line, function, exception type
            time_str = datetime.datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S UTC')
            file = record.pathname.split("/")[-1]
            line = record.lineno
            func = record.funcName
            exc_type = record.exc_info[0].__name__ if record.exc_info else "UnknownError"

            # Optional group + message link
            chat_info = ""
            msg_link = ""
            if hasattr(record, "message_obj") and isinstance(record.message_obj, Message):
                chat = record.message_obj.chat
                msg_id = record.message_obj.id
                if chat.type in ("supergroup", "channel") and chat.username:
                    chat_info = f"<b>Chat:</b> <a href='https://t.me/{chat.username}'>@{chat.username}</a>\n"
                    msg_link = f"<b>Message Link:</b> <a href='https://t.me/{chat.username}/{msg_id}'>Click to View</a>\n"
                else:
                    chat_info = f"<b>Chat ID:</b> <code>{chat.id}</code>\n"

            # Final message
            message = (
                f"<b>⚠️ Error Logged</b>\n"
                f"<b>Time:</b> <code>{time_str}</code>\n"
                f"<b>Level:</b> <code>{record.levelname}</code>\n"
                f"<b>Type:</b> <code>{exc_type}</code>\n"
                f"<b>File:</b> <code>{file}</code>\n"
                f"<b>Function:</b> <code>{func}</code>\n"
                f"<b>Line:</b> <code>{line}</code>\n"
                f"{chat_info}"
                f"{msg_link}"
                f"<b>Message:</b>\n<code>{record.getMessage()}</code>\n\n"
                f"<b>Traceback:</b>\n<code>{tb[:3800]}</code>"
            )

            await self.client.send_message(
                chat_id=OWNER_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        except Exception as e:
            print(f"[Error Handler] Failed to send error notification: {e}")


def setup_error_logging():
    from AnonXMusic import app  # Import your Pyrogram app
    handler = TelegramErrorHandler(app)
    handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(handler)