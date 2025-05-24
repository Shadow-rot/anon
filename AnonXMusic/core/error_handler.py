import datetime
import logging
import traceback
import asyncio
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
        tb = ''.join(traceback.format_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2])) \
            if record.exc_info else "No traceback available."

        # Metadata
        timestamp = record.created
        time_str = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        file = record.pathname.split("/")[-1]
        line = record.lineno
        func = record.funcName
        exc_type = record.exc_info[0].__name__ if record.exc_info else "UnknownError"

        # Format message
        message = (
            "```python\n"
            f"# Error Logged on {time_str}\n"
            f"# Type: {exc_type}\n"
            f"# Level: {record.levelname}\n"
            f"# File: {file} | Line: {line} | Function: {func}\n"
            f"# Message:\n{record.getMessage()}\n\n"
            f"# Traceback:\n{tb[:3800]}\n"
            "```"
        )
        await self.client.send_message(chat_id=OWNER_ID, text=message)
    except Exception as e:
        print(f"[Error Handler] Failed to send error notification: {e}")