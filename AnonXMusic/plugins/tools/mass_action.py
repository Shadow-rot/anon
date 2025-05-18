import asyncio
from asyncio import Semaphore, create_task, gather
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery,
    ChatPermissions, Message
)
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from AnonXMusic import app
from AnonXMusic.misc import SUDOERS

# Concurrency limit (adjust as needed)
MAX_CONCURRENT = 20

def get_keyboard(command):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=f"{command}_yes"),
            InlineKeyboardButton("No", callback_data=f"{command}_no")
        ]
    ])

async def get_group_owner(client, chat_id):
    try:
        async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.status == ChatMemberStatus.OWNER:
                return member.user
    except Exception:
        return None

async def is_owner_or_sudoer(client, chat_id, user_id):
    owner_user = await get_group_owner(client, chat_id)
    if owner_user is None:
        return False, None
    return user_id == owner_user.id or user_id in SUDOERS, owner_user

async def get_bot_member(client, chat_id):
    try:
        return await client.get_chat_member(chat_id, client.me.id)
    except Exception:
        return None

@app.on_message(filters.command(["kickall", "banall", "unbanall", "muteall", "unmuteall", "unpinall"]) & filters.group)
async def group_admin_commands(client: Client, message: Message):
    command = message.command[0]
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_owner, owner_user = await is_owner_or_sudoer(client, chat_id, user_id)
    if not is_owner:
        await message.reply_text(
            f"Sorry {message.from_user.mention}, the '{command}' command can only be executed by the group owner {owner_user.mention}."
        )
        return

    await message.reply(
        f"{message.from_user.mention}, are you sure you want to execute '{command}' in this group?",
        reply_markup=get_keyboard(command)
    )

@app.on_callback_query(filters.regex(r"^(kickall|banall|unbanall|muteall|unmuteall|unpinall)_(yes|no)$"))
async def handle_admin_callback(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    command, action = data.split('_')

    is_owner, owner_user = await is_owner_or_sudoer(client, chat_id, user_id)
    if not is_owner:
        await callback_query.answer("Only the group owner can confirm this action.", show_alert=True)
        return

    if action == "yes":
        await callback_query.message.edit(f"{command.capitalize()} process started...")

        bot_member = await get_bot_member(client, chat_id)
        if not bot_member or bot_member.status != ChatMemberStatus.ADMINISTRATOR:
            await callback_query.message.edit("I need to be an admin to perform this action.")
            return

        required_privileges = {
            'kickall': bot_member.privileges.can_restrict_members,
            'banall': bot_member.privileges.can_restrict_members,
            'unbanall': bot_member.privileges.can_restrict_members,
            'muteall': bot_member.privileges.can_restrict_members,
            'unmuteall': bot_member.privileges.can_restrict_members,
            'unpinall': bot_member.privileges.can_pin_messages,
        }
        if not required_privileges.get(command, False):
            await callback_query.message.edit("I don't have the necessary permissions to perform this action.")
            return

        try:
            if command == "kickall":
                await perform_kick_all(client, chat_id)
            elif command == "banall":
                await perform_ban_all(client, chat_id)
            elif command == "unbanall":
                await perform_unban_all(client, chat_id)
            elif command == "muteall":
                await perform_mute_all(client, chat_id)
            elif command == "unmuteall":
                await perform_unmute_all(client, chat_id)
            elif command == "unpinall":
                await perform_unpin_all(client, chat_id)
        except Exception:
            await callback_query.message.edit(f"An error occurred during {command}.")
    else:
        await callback_query.message.edit(f"{command.capitalize()} process canceled.")

# ========================= Optimized Bulk Functions =========================

async def ban_user(client, chat_id, user_id, sem, counters):
    async with sem:
        try:
            await client.ban_chat_member(chat_id, user_id)
            counters["banned"] += 1
        except Exception:
            counters["errors"] += 1

async def perform_ban_all(client: Client, chat_id):
    sem = Semaphore(MAX_CONCURRENT)
    counters = {"banned": 0, "errors": 0}
    tasks = []

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        tasks.append(create_task(ban_user(client, chat_id, member.user.id, sem, counters)))

    await gather(*tasks)
    await client.send_message(chat_id, f"Banned {counters['banned']} users. Failed: {counters['errors']}.")

async def kick_user(client, chat_id, user_id, sem, counters):
    async with sem:
        try:
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
            counters["kicked"] += 1
        except Exception:
            counters["errors"] += 1

async def perform_kick_all(client: Client, chat_id):
    sem = Semaphore(MAX_CONCURRENT)
    counters = {"kicked": 0, "errors": 0}
    tasks = []

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        tasks.append(create_task(kick_user(client, chat_id, member.user.id, sem, counters)))

    await gather(*tasks)
    await client.send_message(chat_id, f"Kicked {counters['kicked']} users. Failed: {counters['errors']}.")

async def unban_user(client, chat_id, user_id, sem, counters):
    async with sem:
        try:
            await client.unban_chat_member(chat_id, user_id)
            counters["unbanned"] += 1
        except Exception:
            counters["errors"] += 1

async def perform_unban_all(client: Client, chat_id):
    sem = Semaphore(MAX_CONCURRENT)
    counters = {"unbanned": 0, "errors": 0}
    tasks = []

    async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.BANNED):
        tasks.append(create_task(unban_user(client, chat_id, member.user.id, sem, counters)))

    await gather(*tasks)
    await client.send_message(chat_id, f"Unbanned {counters['unbanned']} users. Failed: {counters['errors']}.")

async def mute_user(client, chat_id, user_id, sem, counters, permissions):
    async with sem:
        try:
            await client.restrict_chat_member(chat_id, user_id, permissions)
            counters["muted"] += 1
        except Exception:
            counters["errors"] += 1

async def perform_mute_all(client: Client, chat_id):
    sem = Semaphore(MAX_CONCURRENT)
    counters = {"muted": 0, "errors": 0}
    tasks = []
    permissions = ChatPermissions()

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        tasks.append(create_task(mute_user(client, chat_id, member.user.id, sem, counters, permissions)))

    await gather(*tasks)
    await client.send_message(chat_id, f"Muted {counters['muted']} users. Failed: {counters['errors']}.")

async def unmute_user(client, chat_id, user_id, sem, counters, permissions):
    async with sem:
        try:
            await client.restrict_chat_member(chat_id, user_id, permissions)
            counters["unmuted"] += 1
        except Exception:
            counters["errors"] += 1

async def perform_unmute_all(client: Client, chat_id):
    sem = Semaphore(MAX_CONCURRENT)
    counters = {"unmuted": 0, "errors": 0}
    tasks = []
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
    )

    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            continue
        tasks.append(create_task(unmute_user(client, chat_id, member.user.id, sem, counters, permissions)))

    await gather(*tasks)
    await client.send_message(chat_id, f"Unmuted {counters['unmuted']} users. Failed: {counters['errors']}.")

async def perform_unpin_all(client: Client, chat_id):
    try:
        await client.unpin_all_chat_messages(chat_id)
        await client.send_message(chat_id, "All messages unpinned successfully.")
    except Exception:
        await client.send_message(chat_id, "An error occurred while trying to unpin the messages.")