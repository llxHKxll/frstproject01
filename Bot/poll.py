from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import get_user
from pyrogram.errors import UserNotParticipant
import time

# Admin user ID (change this to the actual bot admin ID)
BOT_ADMIN_ID = 123456789  # Replace with actual bot admin's user ID

polls = {}  # Store polls in memory for the sake of simplicity

def is_bot_admin(user_id):
    """Check if the user is a bot admin."""
    return user_id == BOT_ADMIN_ID

def start_poll(client, message, question, options, expiry_time=None):
    """Start a poll created by bot admin."""
    if not is_bot_admin(message.from_user.id):
        message.reply("You need to be a bot admin to create a poll.")
        return

    poll_id = len(polls) + 1  # Create a new poll ID
    polls[poll_id] = {
        "question": question,
        "options": options,
        "votes": {option: 0 for option in options},
        "voters": set(),  # Set of user IDs who have voted
        "expiry_time": time.time() + (expiry_time * 60) if expiry_time else None,  # Expiry time in seconds
    }

    # Prepare the inline buttons for options
    buttons = [
        [InlineKeyboardButton(option, callback_data=f"vote_{poll_id}_{option}") for option in options]
    ]

    # Send the poll message to the group
    message.reply_text(
        text=f"**Poll:** {question}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def handle_vote(client, callback_query):
    """Handle voting on a poll."""
    data = callback_query.data.split("_")
    poll_id = int(data[1])
    vote_option = data[2]

    if poll_id not in polls:
        callback_query.answer("Poll has ended or does not exist.")
        return

    poll = polls[poll_id]

    # Check if the poll has expired
    if poll["expiry_time"] and time.time() > poll["expiry_time"]:
        callback_query.answer("This poll has expired, you cannot vote anymore.")
        return

    # Prevent multiple votes from the same user
    if callback_query.from_user.id in poll["voters"]:
        callback_query.answer("You've already voted in this poll.")
        return

    # Record the vote
    poll["votes"][vote_option] += 1
    poll["voters"].add(callback_query.from_user.id)  # Add user to the voted list

    callback_query.answer(f"Thanks for voting! You voted for: {vote_option}")

def show_poll_results(client, message, poll_id):
    """Show the results of the poll."""
    if poll_id not in polls:
        message.reply("Invalid poll ID or the poll has ended.")
        return

    poll = polls[poll_id]
    results_text = f"**Poll Results for: {poll['question']}**\n\n"
    
    for option, vote_count in poll['votes'].items():
        results_text += f"{option}: {vote_count} votes\n"

    message.reply_text(results_text)
