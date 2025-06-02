from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from AnonXMusic.utils.data import users_col
from AnonXMusic import app

# Store pending trades and gifts
pending_trades = {}
pending_gifts = {}

# ------------------------ TRADE COMMAND ------------------------ #

@app.on_message(filters.command("trade"))
async def trade(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        return await message.reply_text("You need to reply to a user's message to trade a character!")

    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        return await message.reply_text("You can't trade a character with yourself!")

    if len(message.command) != 3:
        return await message.reply_text("Usage: /trade [Your Character ID] [Other User's Character ID]")

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    sender = await users_col.find_one({'id': sender_id})
    receiver = await users_col.find_one({'id': receiver_id})

    if not sender or not receiver:
        return await message.reply_text("One of the users doesn't have a profile yet!")

    sender_character = next((c for c in sender.get("characters", []) if c['id'] == sender_character_id), None)
    receiver_character = next((c for c in receiver.get("characters", []) if c['id'] == receiver_character_id), None)

    if not sender_character:
        return await message.reply_text("You don't have the character you're trying to trade!")

    if not receiver_character:
        return await message.reply_text("The other user doesn't have the character they're trying to trade!")

    pending_trades[(sender_id, receiver_id)] = (sender_character_id, receiver_character_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Trade", callback_data="confirm_trade")],
        [InlineKeyboardButton("❌ Cancel Trade", callback_data="cancel_trade")]
    ])

    await message.reply_text(
        f"{message.reply_to_message.from_user.mention}, do you accept this trade?",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_trade", "cancel_trade"]))
async def handle_trade_callback(client, callback_query):
    receiver_id = callback_query.from_user.id

    trade_key = next(((sid, rid) for (sid, rid) in pending_trades if rid == receiver_id), None)
    if not trade_key:
        return await callback_query.answer("This is not for you!", show_alert=True)

    sender_id, _ = trade_key
    sender_character_id, receiver_character_id = pending_trades[trade_key]

    sender = await users_col.find_one({'id': sender_id})
    receiver = await users_col.find_one({'id': receiver_id})

    if callback_query.data == "confirm_trade":
        sender_character = next((c for c in sender["characters"] if c["id"] == sender_character_id), None)
        receiver_character = next((c for c in receiver["characters"] if c["id"] == receiver_character_id), None)

        if not sender_character or not receiver_character:
            return await callback_query.message.edit_text("Trade failed. Character not found!")

        sender["characters"].remove(sender_character)
        receiver["characters"].remove(receiver_character)

        sender["characters"].append(receiver_character)
        receiver["characters"].append(sender_character)

        await users_col.update_one({'id': sender_id}, {'$set': {'characters': sender["characters"]}})
        await users_col.update_one({'id': receiver_id}, {'$set': {'characters': receiver["characters"]}})

        del pending_trades[trade_key]

        await callback_query.message.edit_text(
            f"🥳 You have successfully traded your character with {callback_query.message.reply_to_message.from_user.mention}!"
        )

    elif callback_query.data == "cancel_trade":
        del pending_trades[trade_key]
        await callback_query.message.edit_text("❌ Trade cancelled.")


# ------------------------ GIFT COMMAND ------------------------ #

@app.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        return await message.reply_text("Reply to a user's message to gift a character!")

    receiver = message.reply_to_message.from_user
    receiver_id = receiver.id

    if sender_id == receiver_id:
        return await message.reply_text("You can't gift a character to yourself!")

    if len(message.command) != 2:
        return await message.reply_text("Usage: /gift [Character ID]")

    character_id = message.command[1]

    sender = await users_col.find_one({'id': sender_id})
    if not sender:
        return await message.reply_text("You don't have any characters to gift!")

    character = next((c for c in sender.get("characters", []) if c["id"] == character_id), None)
    if not character:
        return await message.reply_text("You don't own this character!")

    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver.username,
        'receiver_first_name': receiver.first_name,
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Gift", callback_data="confirm_gift")],
        [InlineKeyboardButton("❌ Cancel Gift", callback_data="cancel_gift")]
    ])

    await message.reply_text(
        f"Do you really want to gift {receiver.mention} this character?",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_gift", "cancel_gift"]))
async def handle_gift_callback(client, callback_query):
    sender_id = callback_query.from_user.id

    gift_key = next(((sid, rid) for (sid, rid) in pending_gifts if sid == sender_id), None)
    if not gift_key:
        return await callback_query.answer("This is not for you!", show_alert=True)

    sender_id, receiver_id = gift_key
    gift = pending_gifts[gift_key]

    if callback_query.data == "confirm_gift":
        sender = await users_col.find_one({'id': sender_id})
        receiver = await users_col.find_one({'id': receiver_id})

        character = gift["character"]

        if character not in sender.get("characters", []):
            return await callback_query.message.edit_text("Gift failed. Character not in your collection!")

        sender["characters"].remove(character)
        await users_col.update_one({'id': sender_id}, {'$set': {'characters': sender["characters"]}})

        if receiver:
            await users_col.update_one({'id': receiver_id}, {'$push': {'characters': character}})
        else:
            await users_col.insert_one({
                'id': receiver_id,
                'username': gift['receiver_username'],
                'first_name': gift['receiver_first_name'],
                'characters': [character],
            })

        del pending_gifts[gift_key]

        await callback_query.message.edit_text(
            f"You have successfully gifted your character to [{gift['receiver_first_name']}](tg://user?id={receiver_id})!"
        )

    elif callback_query.data == "cancel_gift":
        del pending_gifts[gift_key]
        await callback_query.message.edit_text("❌ Gift cancelled.")