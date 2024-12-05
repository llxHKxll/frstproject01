import time
from datetime import datetime
from database.db_manager import get_user, update_points

def can_claim_daily(user_id):
    """Check if the user can claim their daily reward."""
    user_data = get_user(user_id)
    
    if user_data:
        last_claimed = user_data[6]  # Assuming 6th index for last_claimed time (add to your DB)
        current_time = int(time.time())
        
        # 86400 seconds = 24 hours
        if current_time - last_claimed < 86400:
            return False  # User has already claimed today

    return True

def claim_daily_reward(user_id):
    """Grant daily reward to the user."""
    if can_claim_daily(user_id):
        # Grant points or other rewards here
        reward_points = 100  # Example reward
        update_points(user_id, reward_points)
        
        # Update last_claimed timestamp to current time
        current_time = int(time.time())
        update_last_claimed(user_id, current_time)
        
        return f"🎉 You claimed your daily reward! +{reward_points} points."
    else:
        return "❌ You have already claimed your daily reward today. Come back tomorrow!"
    
def update_last_claimed(user_id, timestamp):
    """Update the last claimed timestamp for the user."""
    from database.db_manager import connect_db
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET last_activity_time = ?
            WHERE user_id = ?
            """,
            (timestamp, user_id),
        )
        conn.commit()
