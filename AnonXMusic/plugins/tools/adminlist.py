import asyncio
from pyrogram import filters, types, enums
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from AnonXMusic import app


@app.on_message(filters.command(["adminlist", "staff"]) & filters.group)
async def adminlist(client, message):
    try:
        owner = None
        admins = []
        total_members = await app.get_chat_members_count(message.chat.id)
        bot_admins = 0
        custom_titles = 0
        promoted_admins = 0

        async for member in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            user = member.user
            if member.status == ChatMemberStatus.OWNER:
                owner = member
            elif user.is_bot:
                bot_admins += 1
            else:
                admins.append(member)
                if member.custom_title:
                    custom_titles += 1
                if member.promoted_by:
                    promoted_admins += 1

        text = f"👮‍♂️ Admin List - {message.chat.title}\n\n"

        # Owner
        if owner:
            user = owner.user
            name = f"@{user.username}" if user.username else user.first_name
            title = f" | {owner.custom_title}" if owner.custom_title else ""
            text += f"💐 Owner: {name}{title}\n\n"

        # Admins
        text += "🛡️ Admins:\n"
        for admin in admins:
            user = admin.user
            name = f"@{user.username}" if user.username else user.first_name
            title = f" | {admin.custom_title}" if admin.custom_title else ""
            promoter = f" (Promoted by: {admin.promoted_by.first_name})" if admin.promoted_by else ""
            text += f"• {name}{title}{promoter}\n"

        total_admins = len(admins) + (1 if owner else 0)

        # Summary stats
        text += "\n─ Group Admin Stats ─\n"
        text += f"👥 Total Members: {total_members}\n"
        text += f"🔢 Admin Count: {total_admins}\n"
        text += f"🤖 Bot Admins: {bot_admins}\n"
        text += f"🎖️ With Titles: {custom_titles}\n"
        text += f"🧑‍⚖️ Promoted Admins: {promoted_admins}\n"

        # Inline keyboard
        buttons = types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton("➕ Add Admin", url=f"https://t.me/{app.me.username}?startgroup=true"),
                types.InlineKeyboardButton("ℹ️ Group Info", callback_data="group_info")
            ],
            [types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_admins")]
        ])

        await message.reply(text, reply_markup=buttons)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        await message.reply(f"Error: {e}")


@app.on_callback_query(filters.regex("refresh_admins"))
async def refresh_admins_callback(client, query):
    await query.answer("Refreshing...", show_alert=False)
    await adminlist(client, query.message)


@app.on_callback_query(filters.regex("group_info"))
async def group_info_callback(client, query):
    chat = await app.get_chat(query.message.chat.id)
    info = f"""ℹ️ Group Info

• Title: {chat.title}
• ID: {chat.id}
• Type: {chat.type.name}
• Members: {chat.members_count}
• Description: {chat.description or "No description."}
"""
    await query.answer()
    await query.message.reply(info)