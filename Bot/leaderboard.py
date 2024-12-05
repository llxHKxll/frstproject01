from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import get_group_members  # Assuming this fetches sorted members

# Store the current leaderboard mode for each chat (points or level)
leaderboard_modes = {}

@app.on_message(filters.command("leaderboard"))
async def leaderboard_handler(client, message):
    chat_id = message.chat.id
    
    # Default to points if no leaderboard mode is set
    if chat_id not in leaderboard_modes:
        leaderboard_modes[chat_id] = "points"

    leaderboard_type = leaderboard_modes[chat_id]  # Get current mode (points or level)
    leaderboard_data = get_group_members(chat_id, leaderboard_type)  # Get the leaderboard data sorted by points or level
    
    # Create leaderboard message text
    leaderboard_text = f"🏆 **Leaderboard based on {leaderboard_type.capitalize()}** 🏆\n\n"
    for i, user in enumerate(leaderboard_data, start=1):
        leaderboard_text += f"{i}. {user[1]} - {user[2]}\n"  # username and points/level

    # Create inline buttons for switching between points and levels
    buttons = [
        [
            InlineKeyboardButton("Points Leaderboard", callback_data="points"),
            InlineKeyboardButton("Level Leaderboard", callback_data="level"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Send the leaderboard message or edit if already sent
    if 'leaderboard_message_id' in message.chat:
        await client.edit_message_text(
            chat_id, 
            message.chat['leaderboard_message_id'],
            leaderboard_text,
            reply_markup=reply_markup
        )
    else:
        msg = await message.reply_text(leaderboard_text, reply_markup=reply_markup)
        message.chat['leaderboard_message_id'] = msg.message_id  # Save the message ID for future edits

@app.on_callback_query(filters.regex("points|level"))
async def leaderboard_switch_handler(client, callback_query):
    chat_id = callback_query.message.chat.id
    leaderboard_type = callback_query.data  # Either "points" or "level"

    # Update the leaderboard mode for this chat
    leaderboard_modes[chat_id] = leaderboard_type

    # Get the updated leaderboard data
    leaderboard_data = get_group_members(chat_id, leaderboard_type)

    # Create leaderboard message text
    leaderboard_text = f"🏆 **Leaderboard based on {leaderboard_type.capitalize()}** 🏆\n\n"
    for i, user in enumerate(leaderboard_data, start=1):
        leaderboard_text += f"{i}. {user[1]} - {user[2]}\n"  # username and points/level

    # Edit the message with the new leaderboard data
    buttons = [
        [
            InlineKeyboardButton("Points Leaderboard", callback_data="points"),
            InlineKeyboardButton("Level Leaderboard", callback_data="level"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await client.edit_message_text(
        chat_id,
        callback_query.message.message_id,
        leaderboard_text,
        reply_markup=reply_markup
    )

    # Acknowledge the callback query
    await callback_query.answer()
