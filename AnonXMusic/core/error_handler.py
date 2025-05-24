import logging
import traceback
import asyncio
import datetime
from pyrogram import Client
from config import OWNER_ID  # Ensure this is an int

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

            # Extra metadata
            time_str = datetime.datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S UTC')
            file = record.pathname.split("/")[-1]
            line = record.lineno
            func = record.funcName
            exc_type = record.exc_info[0].__name__ if record.exc_info else "UnknownError"

            # Final formatted message
            message = (
                f"Error Logged on {time_str}\n\n"
                f"Level: {record.levelname}\n"
                f"Type: {exc_type}\n"
                f"File: {file}\n"
                f"Function: {func}\n"
                f"Line: {line}\n"
                f"Message: {record.getMessage()}\n\n"
                f"Traceback:\n{tb[:3800]}"
            )

            await self.client.send_message(chat_id=OWNER_ID, text=message)
        except Exception as e:
            print(f"[Error Handler] Failed to send error notification: {e}")

def setup_error_logging():
    from AnonXMusic import app  # Your Pyrogram Client instance
    handler = TelegramErrorHandler(app)
    handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(handler)