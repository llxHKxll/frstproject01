import time
from database.db_manager import get_user  # Make sure you import your database functions

# Store the last time a user sent a message
USER_LAST_MESSAGE_TIME = {}

def check_flood(user_id):
    """Check if the user is flooding (sending messages too quickly)."""
    current_time = time.time()

    if user_id in USER_LAST_MESSAGE_TIME:
        last_time = USER_LAST_MESSAGE_TIME[user_id]
        # If the user sends more than 2 messages in 5 seconds, block them for 10 seconds
        if current_time - last_time < 1:  # Less than 1 seconds since last message
            return True  # Block the user
    USER_LAST_MESSAGE_TIME[user_id] = current_time  # Update the last message time
    return False
