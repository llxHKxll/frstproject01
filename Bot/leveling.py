import time
from database.db_manager import get_user, update_user_data

def level_up(user_id, message_text):
    """Track experience and level for a user based on their messages."""
    user_data = get_user(user_id)
    
    if user_data:
        # Exp based on message length
        exp_gained = 2  # Experience based on word count
        
        # Check if XP booster is active
        xp_booster_expiry = user_data[8]  # Get the expiry time of the XP booster
        if xp_booster_expiry > time.time():
            exp_gained *= 2  # Double the XP if booster is active
        
        new_exp = user_data[4] + exp_gained  # Adding the gained exp to current exp
        new_level = new_exp // 100  # Every 100 exp points increase the level

        # Prevent level from decreasing
        if new_level < user_data[3]:
            new_level = user_data[3]

        # Update the user data in the database
        update_user_data(user_id, new_exp, new_level)
        print(f"User {user_id} leveled up to level {new_level} with {new_exp} exp.")
