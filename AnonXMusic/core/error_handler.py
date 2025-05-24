from AnonXMusic import app  # Your pyrogram Client instance
from AnonXMusic.core.error_notifier import TelegramErrorHandler
import logging

def setup_error_logging():
    handler = TelegramErrorHandler(app)
    handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(handler)

setup_error_logging()