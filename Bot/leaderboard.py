from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import get_group_members  # Fetch users sorted by points or level

# Store the current leaderboard mode for each chat
leaderboard_modes = {}

def get_leaderboard_data(chat_id, leaderboard_type):
    """Fetch leaderboard data sorted by points or levels."""
    # Get the sorted leaderboard data from the database
    return get_group_members(chat_id, leaderboard_type)

def prepare_leaderboard_message(chat_id, leaderboard_type):
    """Prepare the leaderboard message based on the type (points or level)."""
    leaderboard_data = get_leaderboard_data(chat_id, leaderboard_type)
    
    # Prepare the leaderboard text
    leaderboard_text = f"🏆 **Leaderboard based on {leaderboard_type.capitalize()}** 🏆\n\n"
    for i, user in enumerate(leaderboard_data, start=1):
        leaderboard_text += f"{i}. {user[1]} - {user[2]}\n"  # username and points/level

    # Prepare the inline buttons to switch between leaderboards
    buttons = [
        [
            InlineKeyboardButton("Points Leaderboard", callback_data="points"),
            InlineKeyboardButton("Level Leaderboard", callback_data="level"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    return leaderboard_text, reply_markup

def update_leaderboard_message(client, callback_message, chat_id, leaderboard_type):
    """Fetch and edit the leaderboard message based on the selected leaderboard type."""
    leaderboard_text, reply_markup = prepare_leaderboard_message(chat_id, leaderboard_type)
    
    # Edit the message instead of sending a new one
    client.edit_message_text(
        chat_id,
        callback_message.id,  # Corrected here
        leaderboard_text,
        reply_markup=reply_markup
    )
