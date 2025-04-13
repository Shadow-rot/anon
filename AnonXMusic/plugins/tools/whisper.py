from pyrogram import Client, filters
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from uuid import uuid4

from AnonXMusic import app  # change to your actual bot instance if needed


@app.on_inline_query()
async def whisper_inline(client, inline_query):
    query = inline_query.query.strip()

    if not query.lower().startswith("whisper @"):
        return await inline_query.answer([], switch_pm_text="type like: whisper @username message", switch_pm_parameter="start")

    try:
        parts = query.split(" ", 2)
        if len(parts) < 3:
            return await inline_query.answer([], switch_pm_text="use format: whisper @user text", switch_pm_parameter="start")

        username = parts[1].lstrip("@")
        message = parts[2]

        result = InlineQueryResultArticle(
            title=f"whisper to @{username}",
            description="tap to reveal secret message",
            input_message_content=InputTextMessageContent("🔐 tap to reveal the secret message"),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🕵️ reveal message", callback_data=f"whisper|{username}|{message}")]]
            ),
            id=str(uuid4())
        )

        await inline_query.answer([result], cache_time=0)

    except Exception as e:
        print(f"[Inline Whisper Error] {e}")
        await inline_query.answer([], cache_time=1)


@app.on_callback_query(filters.regex(r"^whisper\|"))
async def reveal_secret(client: Client, callback_query: CallbackQuery):
    data = callback_query.data.split("|", 2)
    target_username = data[1]
    secret_message = data[2]
    from_user = callback_query.from_user

    if from_user.username and from_user.username.lower() == target_username.lower():
        await callback_query.message.edit_text(
            f"🔓 secret message for @{target_username}:\n\n{secret_message}"
        )
    else:
        await callback_query.answer("this message isn't for you!", show_alert=True)