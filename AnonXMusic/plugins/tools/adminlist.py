import asyncio
from pyrogram import filters, types
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from AnonXMusic import app
from AnonXMusic.utils.autofix import auto_fix_handler  # ✅ Importing the decorator

# /adminlist command
@app.on_message(filters.command(["adminlist", "staff"]) & filters.group)
@auto_fix_handler
async def adminlist(client, message):
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
    if owner:
        user = owner.user
        name = f"@{user.username}" if user.username else user.first_name
        title = f" | {owner.custom_title}" if owner.custom_title else ""
        text += f"💐 Owner: {name}{title}\n\n"

    text += "🛡️ Admins:\n"
    for admin in admins:
        user = admin.user
        name = f"@{user.username}" if user.username else user.first_name
        title = f" | {admin.custom_title}" if admin.custom_title else ""
        promoter = f" (Promoted by: {admin.promoted_by.first_name})" if admin.promoted_by else ""
        text += f"• {name}{title}{promoter}\n"

    total_admins = len(admins) + (1 if owner else 0)

    text += "\n─ Group Stats ─\n"
    text += f"👥 Members: {total_members}\n"
    text += f"🔢 Admins: {total_admins}\n"
    text += f"🤖 Bot Admins: {bot_admins}\n"
    text += f"🎖️ With Titles: {custom_titles}\n"
    text += f"🧑‍⚖️ Promoted Admins: {promoted_admins}\n"
    text += "\n💡 To add new admins: Open group > Manage Group > Administrators"

    buttons = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("➕ Add Admin", url=f"https://t.me/{app.me.username}?startgroup=true"),
            types.InlineKeyboardButton("ℹ️ Group Info", callback_data="group_info")
        ],
        [
            types.InlineKeyboardButton("🔄 Refresh", callback_data="refresh_admins"),
            types.InlineKeyboardButton("🤖 Bot List", callback_data="botlist")
        ],
        [types.InlineKeyboardButton("📛 Deleted Accounts", callback_data="deleted_list")]
    ])

    await message.reply(text, reply_markup=buttons)


@app.on_callback_query(filters.regex("refresh_admins"))
@auto_fix_handler
async def refresh_admins_callback(client, query):
    await query.answer("Refreshing...")
    await adminlist(client, query.message)


@app.on_callback_query(filters.regex("group_info"))
@auto_fix_handler
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


@app.on_callback_query(filters.regex("botlist"))
@auto_fix_handler
async def bot_list(client, query):
    bots = []
    async for member in app.get_chat_members(query.message.chat.id):
        if member.user.is_bot:
            bots.append(f"🤖 {member.user.first_name} [@{member.user.username or 'N/A'}]")

    await query.answer()
    if not bots:
        return await query.message.reply("No bots found in this group.")
    await query.message.reply("🤖 Bot List:\n" + "\n".join(bots))


@app.on_callback_query(filters.regex("deleted_list"))
@auto_fix_handler
async def deleted_list(client, query):
    deleted = []
    async for member in app.get_chat_members(query.message.chat.id):
        if member.user.is_deleted:
            deleted.append("📛 Deleted Account")

    await query.answer()
    if not deleted:
        return await query.message.reply("No deleted accounts found.")
    await query.message.reply(f"Found {len(deleted)} deleted accounts.\n" + "\n".join(deleted))