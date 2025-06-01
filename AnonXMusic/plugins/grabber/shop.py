from pyrogram import Client, filters
from pyrogram.types import Message
from AnonXMusic import app
from AnonXMusic.utils.data import users_col, collection

# Rarity coin cost mapping
rarity_coin_mapping = {
    "🟢 Common": 2000000,
    "🔵 Medium": 4000000,
    "🟠 Rare": 8000000,
    "🟡 Legendary": 1500000,
    "🪽 celestial": 20000000,
    "💮 Exclusive": 300000000,
    "🥴 Spacial": 400000000000,
    "💎 Premium": 2000000000000000000,
    "🔮 Limited": 6000000000000000000,
}

@app.on_message(filters.command("buy") & filters.private)
async def buy_handler(client: Client, message: Message):
    user_id = message.from_user.id
    args = message.command

    if len(args) != 2:
        return await message.reply("Please provide a valid pick ID to buy. Example: /buy <id>")

    character_id = args[1]

    character = await collection.find_one({'id': character_id})
    if not character:
        return await message.reply("Pick not found in the store.")

    user = await user_collection.find_one({'id': user_id})
    if not user or 'balance' not in user:
        return await message.reply("Error: User balance not found.")

    rarity = character.get('rarity', 'Unknown Rarity')
    coin_cost = rarity_coin_mapping.get(rarity, 0)

    if coin_cost == 0:
        return await message.reply("Invalid rarity. Cannot determine the coin cost.")

    if user['balance'] < coin_cost:
        return await message.reply("You don't have enough coins to buy this character.")

    # Update user collection
    await user_collection.update_one(
        {'id': user_id},
        {
            '$push': {'characters': character},
            '$inc': {'balance': -coin_cost}
        }
    )

    img_url = character.get('image_url', None)
    text = f"Success! You have purchased {character['name']} for {coin_cost} coins."

    if img_url:
        await message.reply_photo(photo=img_url, caption=text)
    else:
        await message.reply(text)

@app.on_message(filters.command("store") & filters.private)
async def store_handler(client: Client, message: Message):
    msg = (
        "🛒 **Waifu Shop** - Available Characters:\n\n"
        "🟢 Common: Ŧ20,00,000 💸\n"
        "🔵 Medium: Ŧ40,00,000 💸\n"
        "🟠 Rare: Ŧ80,00,000 💸\n"
        "🟡 Legendary: Ŧ15,00,000 💸\n"
        "🪽 celestial: Ŧ20,000,000 💸\n"
        "💮 Exclusive: Ŧ300,000,000 💸\n"
        "🥴 Spacial: Ŧ4000,0000,0000 💸\n"
        "💎 Premium: Ŧ2000000000000000000 💸\n"
        "🔮 Limited: Ŧ6000000000000000000 💸\n\n"
        "To purchase, use:\n`/buy <pick_id>`"
    )
    await message.reply(msg)