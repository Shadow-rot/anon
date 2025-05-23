import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, ChatTypeFilter
from aiogram.client.default import DefaultBotProperties
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set in .env file

router = Router()

@router.message(Command("bots"), ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]))
async def list_bots(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    bot_members = []

    async for member in bot.get_chat_administrators(chat_id):
        if member.user.is_bot:
            bot_members.append(member.user)

    if not bot_members:
        return await message.answer("No bots found in this group.")

    text = f"ʙᴏᴛ ʟɪsᴛ - {message.chat.title}\n\n🤖 ʙᴏᴛs\n"
    for i, b in enumerate(bot_members):
        prefix = "└" if i == len(bot_members) - 1 else "├"
        text += f"{prefix} @{b.username or b.full_name}\n"

    text += f"\nᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ʙᴏᴛs: {len(bot_members)}"
    await message.answer(text)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())