import asyncio
from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from AnonXMusic import app


@app.on_message(filters.command(["adminlist", "staff"]) & filters.group)
async def adminlist(client, message):
    try:
        owner = None
        admins = []

        async for member in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            user = member.user

            if user.is_bot:
                continue

            if member.status == enums.ChatMemberStatus.OWNER:
                owner = member
            else:
                admins.append(member)

        text = f"👮‍♂️ ᴀᴅᴍɪɴ ʟɪsᴛ - {message.chat.title}\n\n"

        # Owner
        if owner:
            user = owner.user
            name = f"@{user.username}" if user.username else user.first_name
            title = f" - {owner.custom_title}" if owner.custom_title else ""
            text += f"💐 ᴏᴡɴᴇʀ: {name}{title}\n\n"

        # Admins
        text += "🛡️ ᴀᴅᴍɪɴs:\n"
        for admin in admins[:-1]:
            user = admin.user
            name = f"@{user.username}" if user.username else user.first_name
            title = f" - {admin.custom_title}" if admin.custom_title else ""
            text += f"├ {name}{title}\n"

        if admins:
            last = admins[-1]
            user = last.user
            name = f"@{user.username}" if user.username else user.first_name
            title = f" - {last.custom_title}" if last.custom_title else ""
            text += f"└ {name}{title}\n"

        total = len(admins) + (1 if owner else 0)
        text += f"\nᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs: {total}"

        await app.send_message(message.chat.id, text)

    except FloodWait as e:
        await asyncio.sleep(e.value)