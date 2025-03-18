from asyncio import sleep
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message
from AnonXMusic import app

# Define your bot owner(s)
BOT_OWNER = [5147822244]  # Replace with your Telegram user ID(s)

# Admin filter allowing bot owners
class AdminOrOwnerFilter(filters.Filter):
    async def __call__(self, _, __, message: Message):
        if message.from_user and message.from_user.id in BOT_OWNER:
            return True
        if not message.chat:
            return False
        member = await message.chat.get_member(message.from_user.id)
        return member.status in ("administrator", "creator")

admin_filter = AdminOrOwnerFilter()


@app.on_message(filters.command("purge") & admin_filter)
async def purge(app: app, msg: Message):
    if msg.chat.type != ChatType.SUPERGROUP:
        await msg.reply_text(text="**ɪ ᴄᴀɴ'ᴛ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ. ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ.**")
        return

    if msg.reply_to_message:
        message_ids = list(range(msg.reply_to_message.id, msg.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i: i + n]

        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await app.delete_messages(chat_id=msg.chat.id, message_ids=plist, revoke=True)
            await msg.delete()
        except MessageDeleteForbidden:
            await msg.reply_text("**ɪ ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs. ᴍᴇssᴀɢᴇs ᴍᴀʏ ʙᴇ ᴏʟᴅ, ᴏʀ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴs.**")
            return
        except RPCError as ef:
            await msg.reply_text(f"**ᴇʀʀᴏʀ:** <code>{ef}</code>")
            return

        count_del_msg = len(message_ids)
        done = await msg.reply_text(f"ᴅᴇʟᴇᴛᴇᴅ <i>{count_del_msg}</i> ᴍᴇssᴀɢᴇs")
        await sleep(3)
        await done.delete()
    else:
        await msg.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢᴇ !**")


@app.on_message(filters.command("spurge") & admin_filter)
async def spurge(app: app, msg: Message):
    if msg.chat.type != ChatType.SUPERGROUP:
        await msg.reply_text(text="**ɪ ᴄᴀɴ'ᴛ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ. ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ.**")
        return

    if msg.reply_to_message:
        message_ids = list(range(msg.reply_to_message.id, msg.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i: i + n]

        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await app.delete_messages(chat_id=msg.chat.id, message_ids=plist, revoke=True)
            await msg.delete()
        except MessageDeleteForbidden:
            await msg.reply_text("**ɪ ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs. ᴍᴇssᴀɢᴇs ᴍᴀʏ ʙᴇ ᴏʟᴅ, ᴏʀ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴs.**")
            return
        except RPCError as ef:
            await msg.reply_text(f"**ᴇʀʀᴏʀ:** <code>{ef}</code>")
            return
    else:
        await msg.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢᴇ !**")


@app.on_message(filters.command("del") & admin_filter)
async def del_msg(app: app, msg: Message):
    if msg.chat.type != ChatType.SUPERGROUP:
        await msg.reply_text(text="**ɪ ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ. ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ.**")
        return

    if msg.reply_to_message:
        await msg.delete()
        await app.delete_messages(chat_id=msg.chat.id, message_ids=msg.reply_to_message.id)
    else:
        await msg.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ.**")