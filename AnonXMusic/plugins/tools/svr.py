import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from config import OWNER_ID
from AnonXMusic import app
from AnonXMusic.server_reporter import auto_report


@app.on_message(filters.command("startreport") & filters.user(OWNER_ID))
async def start_server_report(_, message: Message):
    asyncio.create_task(auto_report())
    await message.reply_text(
        "✅ <b>Server Reporter Started!</b>\nYou'll receive updates every 5 minutes.",
        parse_mode=ParseMode.HTML,
    )