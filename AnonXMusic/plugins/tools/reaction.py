from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app  # Or use your own `Client(...)` instance


# Keywords mapped to emoji reactions
EMOJI_REACTIONS = {
    "hello": "👋",
    "bye": "👍",
    "love": "❤️",
    "lol": "😂",
    "sad": "😢",
    "angry": "😠",
    "cool": "🔥",
}


@app.on_message(filters.text & filters.group)
async def react_with_emoji(client, message: Message):
    text = message.text.lower()

    # Get allowed reaction emojis for the group
    chat = await app.get_chat(message.chat.id)
    allowed_reactions = chat.available_reactions or []

    # Loop through keywords
    for keyword, emoji in EMOJI_REACTIONS.items():
        if keyword in text:
            # Only send the emoji if it's allowed
            if emoji in allowed_reactions:
                await app.send_reaction(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    emoji=emoji
                )
            break