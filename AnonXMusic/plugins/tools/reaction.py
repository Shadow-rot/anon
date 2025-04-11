from pyrogram import filters
from pyrogram.types import Message
from pyrogram.types.chat_reactions import AllReactions, SomeReactions
from AnonXMusic import app


# Emoji reactions per keyword
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
    chat = await app.get_chat(message.chat.id)
    reactions = chat.available_reactions

    for keyword, emoji in EMOJI_REACTIONS.items():
        if keyword in text:
            # If all reactions are allowed, send any
            if isinstance(reactions, AllReactions) or (
                isinstance(reactions, SomeReactions) and emoji in reactions.reactions
            ):
                await app.send_reaction(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    emoji=emoji
                )
            break