from pyrogram import filters
from pyrogram.types import Message
from AnonXMusic import app


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
            # Reactions can be:
            # - None (reactions not allowed)
            # - list of emojis (SomeReactions)
            # - string 'all' (some older versions)
            # - object with .reactions attribute
            if reactions is None:
                break  # Reactions not allowed in this chat

            if hasattr(reactions, "reactions"):  # SomeReactions
                if emoji in reactions.reactions:
                    await app.send_reaction(message.chat.id, message.id, emoji)
            elif isinstance(reactions, list):  # Already a list
                if emoji in reactions:
                    await app.send_reaction(message.chat.id, message.id, emoji)
            else:
                # fallback: assume all reactions allowed
                await app.send_reaction(message.chat.id, message.id, emoji)
            break