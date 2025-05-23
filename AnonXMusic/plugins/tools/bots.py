import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8111617507:AAHPKqyDoXGouCSUGKsO1JCge4VdFJuuyAE"  # Replace with your bot token

dp = Dispatcher()

@dp.message(Command("bots"), F.chat.type == ChatType.GROUP)
async def get_bots_list(message: Message, bot: Bot):
    try:
        chat_id = message.chat.id
        bots = []
        async for member in bot.get_chat_administrators(chat_id):
            if member.user.is_bot:
                bots.append(member.user)

        if not bots:
            return await message.answer("No bots found in this group.")

        response = f"ʙᴏᴛ ʟɪsᴛ - {message.chat.title}\n\n🤖 ʙᴏᴛs\n"
        for i, b in enumerate(bots):
            branch = "└" if i == len(bots) - 1 else "├"
            response += f"{branch} @{b.username or b.first_name}\n"

        response += f"\nᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ʙᴏᴛs: {len(bots)}"
        await message.answer(response)

    except Exception as e:
        await message.answer(f"Error: {e}")


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())