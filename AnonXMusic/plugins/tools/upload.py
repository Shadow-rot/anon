"""
import urllib.request
from pymongo import ReturnDocument
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from AnonXMusic import app
from AnonXMusic.config import LOGGER_ID as CHARA_CHANNEL_ID
from AnonXMusic.utils.harem_db import collection, db

async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']

async def upload(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) != 4:
            await update.message.reply_text("""
Wrong ❌️ format...  eg. /upload Img_url muzan-kibutsuji Demon-slayer 3

img_url character-name anime-name rarity-number

use rarity number accordingly rarity Map:

1:🟢 𝘾𝙤𝙢𝙢𝙤𝙣, 2:🔵 𝙈𝙚𝙙𝙞𝙪𝙢, 3:🟡 𝙍𝙖𝙧𝙚, 4:🔴 𝙇𝙚𝙜𝙚𝙣𝙙𝙖𝙧𝙮, 5:💠 𝙎𝙥𝙚𝙘𝙞𝙖𝙡, 6:🔮 𝙇𝙞𝙢𝙞𝙩𝙚𝙙, 7:❄️𝙒𝙞𝙣𝙩𝙚𝙧
""")
            return

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        try:
            urllib.request.urlopen(args[0])
        except:
            await update.message.reply_text('Invalid URL.')
            return

        rarity_map = {
            1: "🟢 𝘾𝙤𝙢𝙢𝙤𝙣", 2: "🔵 𝙈𝙚𝙙𝙞𝙪𝙢", 3: "🟡 𝙍𝙖𝙧𝙚",
            4: "🔴 𝙇𝙚𝙜𝙚𝙣𝙙𝙖𝙧𝙮", 5: "💠 𝙎𝙥𝙚𝙘𝙞𝙖𝙡",
            6: "🔮 𝙇𝙞𝙢𝙞𝙩𝙚𝙙", 7: "❄️𝙒𝙞𝙣𝙩𝙚𝙧"
        }

        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            await update.message.reply_text('Invalid rarity. Use 1–7 only.')
            return

        char_id = str(await get_next_sequence_number('character_id')).zfill(2)

        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'id': char_id
        }

        message = await context.bot.send_photo(
            chat_id=CHARA_CHANNEL_ID,
            photo=args[0],
            caption=(
                f"<b>Waifu Name:</b> {character_name}\n"
                f"<b>Anime Name:</b> {anime}\n"
                f"<b>Quality:</b> {rarity}\n"
                f"<b>ID:</b> {char_id}\n"
                f"Added by <a href=\"tg://user?id={update.effective_user.id}\">{update.effective_user.first_name}</a>"
            )
        )

        character['message_id'] = message.message_id
        await collection.insert_one(character)

        await update.message.reply_text('✅ Waifu added successfully.')
    except Exception as e:
        await update.message.reply_text(f'❌ Failed to upload. Error: {str(e)}')

async def delete(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Usage: /delete ID')
            return

        character = await collection.find_one_and_delete({'id': args[0]})

        if character:
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            await update.message.reply_text('✅ Character deleted successfully.')
        else:
            await update.message.reply_text('Character deleted from DB, but not found in channel.')
    except Exception as e:
        await update.message.reply_text(f'❌ Error: {str(e)}')

async def update(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Usage: /update id field new_value')
            return

        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text('Character not found.')
            return

        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        field = args[1]
        if field not in valid_fields:
            await update.message.reply_text(f'Invalid field. Choose from: {", ".join(valid_fields)}')
            return

        new_value = args[2]
        if field in ['name', 'anime']:
            new_value = new_value.replace('-', ' ').title()
        elif field == 'rarity':
            rarity_map = {
                1: "🟢 𝘾𝙤𝙢𝙢𝙤𝙣", 2: "🔵 𝙈𝙚𝙙𝙞𝙪𝙢", 3: "🟡 𝙍𝙖𝙧𝙚",
                4: "🔴 𝙇𝙚𝙜𝙚𝙣𝙙𝙖𝙧𝙮", 5: "💠 𝙎𝙥𝙚𝙘𝙞𝙖𝙡",
                6: "🔮 𝙇𝙞𝙢𝙞𝙩𝙚𝙙", 7: "❄️𝙒𝙞𝙣𝙩𝙚𝙧"
            }
            try:
                new_value = rarity_map[int(new_value)]
            except KeyError:
                await update.message.reply_text('Invalid rarity. Use 1–7.')
                return

        await collection.find_one_and_update({'id': args[0]}, {'$set': {field: new_value}})

        if field == 'img_url':
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            msg = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=new_value,
                caption=(
                    f"<b>Character Name:</b> {character['name']}\n"
                    f"<b>Anime Name:</b> {character['anime']}\n"
                    f"<b>Rarity:</b> {character['rarity']}\n"
                    f"<b>ID:</b> {character['id']}\n"
                    f"Updated by <a href=\"tg://user?id={update.effective_user.id}\">{update.effective_user.first_name}</a>"
                )
            )
            await collection.find_one_and_update({'id': args[0]}, {'$set': {'message_id': msg.message_id}})
        else:
            updated_character = await collection.find_one({'id': args[0]})
            await context.bot.edit_message_caption(
                chat_id=CHARA_CHANNEL_ID,
                message_id=character['message_id'],
                caption=(
                    f"<b>Character Name:</b> {updated_character['name']}\n"
                    f"<b>Anime Name:</b> {updated_character['anime']}\n"
                    f"<b>Rarity:</b> {updated_character['rarity']}\n"
                    f"<b>ID:</b> {updated_character['id']}\n"
                    f"Updated by <a href=\"tg://user?id={update.effective_user.id}\">{update.effective_user.first_name}</a>"
                )
            )

        await update.message.reply_text('✅ Character updated. Caption may take time to reflect.')
    except Exception as e:
        await update.message.reply_text('❌ Update failed. Possible reasons: bot not in channel, wrong ID, or old message.')

# Register handlers
UPLOAD_HANDLER = CommandHandler('upload', upload, block=False)
DELETE_HANDLER = CommandHandler('delete', delete, block=False)
UPDATE_HANDLER = CommandHandler('update', update, block=False)

app.add_handler(UPLOAD_HANDLER)
app.add_handler(DELETE_HANDLER)
app.add_handler(UPDATE_HANDLER)


"""