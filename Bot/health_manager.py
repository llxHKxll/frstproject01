from database.db_manager import get_user, update_health

def reduce_health(user_id, amount):
    """Reduce health by a specified amount."""
    user_data = get_user(user_id)
    if not user_data:
        return "User not found."
    
    current_health = user_data[5]  # Assuming health is at index 5
    new_health = max(0, current_health - amount)  # Ensure health doesn't go below 0
    update_health(user_id, new_health)
    return new_health

def recover_health(user_id, amount):
    """Recover health by a specified amount."""
    user_data = get_user(user_id)
    if not user_data:
        return "User not found."
    
    current_health = user_data[5]
    new_health = min(100, current_health + amount)  # Ensure health doesn't exceed 100
    update_health(user_id, new_health)
    return new_health

def get_health(user_id):
    """Get the current health of a user."""
    user_data = get_user(user_id)
    if not user_data:
        return None
    return user_data[5]
