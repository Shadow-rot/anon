import logging
import traceback
import asyncio
from pyrogram import Client
from config import OWNER_ID  # Ensure this is an `int`

class TelegramErrorHandler(logging.Handler):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            asyncio.create_task(self.send_error(record))

    async def send_error(self, record):
        try:
            tb = ''.join(traceback.format_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2])) \
                if record.exc_info else "No traceback available."

            message = (
                f"**Error Logged:**\n\n"
                f"`{record.levelname}`: `{record.getMessage()}`\n\n"
                f"**Traceback:**\n"
                f"```{tb[:3800]}```"  # truncate to avoid Telegram limits
            )
            await self.client.send_message(chat_id=OWNER_ID, text=message)
        except Exception as e:
            print(f"[Error Handler] Failed to send error notification: {e}")

def setup_error_logging():
    from AnonXMusic import app  # pyrogram Client
    handler = TelegramErrorHandler(app)
    handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(handler)