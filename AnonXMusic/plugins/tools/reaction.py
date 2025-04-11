from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app


# Emoji reactions
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

    # Ensure reactions are valid and not None
    if reactions is None:
        return  # No reactions allowed in this chat

    # Handle cases when reactions are in list form or have an attribute `.reactions`
    for keyword, emoji in EMOJI_REACTIONS.items():
        if keyword in text:
            # Check if reactions are a list of valid emojis
            if isinstance(reactions, list):
                if emoji in reactions:
                    await app.send_reaction(
                        chat_id=message.chat.id,
                        message_id=message.id,
                        emoji=emoji
                    )
            # Check if reactions have a `.reactions` attribute (SomeReactions)
            elif hasattr(reactions, "reactions"):
                if emoji in reactions.reactions:
                    await app.send_reaction(
                        chat_id=message.chat.id,
                        message_id=message.id,
                        emoji=emoji
                    )
            else:
                # Fallback if reactions are in an unexpected form, assume all allowed
                await app.send_reaction(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    emoji=emoji
                )
            break  # Only react to the first match