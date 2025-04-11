"""from pyrogram import filters
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

    if reactions is None:
        return  # Reactions not allowed in this chat

    for keyword, emoji in EMOJI_REACTIONS.items():
        if keyword in text:
            try:
                # Case 1: Reactions is a list of emojis
                if isinstance(reactions, list) and emoji in reactions:
                    await app.send_reaction(message.chat.id, message.id, emoji)
                    break

                # Case 2: Object with `.reactions` attribute (SomeReactions)
                elif hasattr(reactions, "reactions") and reactions.reactions:
                    if emoji in reactions.reactions:
                        await app.send_reaction(message.chat.id, message.id, emoji)
                        break

                # Case 3: Unknown format – assume all emojis allowed
                elif not hasattr(reactions, "reactions"):
                    await app.send_reaction(message.chat.id, message.id, emoji)
                    break

            except Exception as e:
                print(f"[Reaction Error] {e}")
            break"""