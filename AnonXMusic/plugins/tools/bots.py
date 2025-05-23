import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatType
from aiogram.filters import Command, ChatTypeFilter
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8111617507:AAHPKqyDoXGouCSUGKsO1JCge4VdFJuuyAE"  # Replace with your bot token

dp = Dispatcher()

@dp.message(Command("bots"), ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP]))
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())