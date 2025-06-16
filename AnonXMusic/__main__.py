import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AnonXMusic import LOGGER, app, userbot
from AnonXMusic.core.call import Anony
from AnonXMusic.misc import sudo
from AnonXMusic.plugins import ALL_MODULES
from AnonXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

from AnonXMusic.core.error_handler import setup_error_logging
from server_reporter import run_reporter


async def init():
    setup_error_logging()

    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).error(f"Failed to load banned users: {e}")

    await app.start()

    # ✅ Import all plugin modules
    for all_module in ALL_MODULES:
        importlib.import_module("AnonXMusic.plugins." + all_module)

    LOGGER("AnonXMusic.plugins").info("Successfully Imported Modules...")

    await userbot.start()
    await Anony.start()

    try:
        await Anony.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AnonXMusic").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except Exception as e:
        LOGGER(__name__).error(f"Error during stream call: {e}")

    await Anony.decorators()

    asyncio.create_task(run_reporter())

    LOGGER("AnonXMusic").info(
        "Alex Started Successfully.\n\nDon't forget to visit @the_losthope"
    )

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("AnonXMusic").info("Stopping AnonX Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())