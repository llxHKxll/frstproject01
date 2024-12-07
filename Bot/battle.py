import random
import time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db_manager import get_user, update_points, update_health, deduct_health

# battle.py

active_battles = {}  # Keep track of all ongoing battles

def start_battle(user_a, user_b):
    """Start a battle between two users."""
    active_battles[user_a] = {
        "opponent": user_b,
        "turn": user_a,  # User A's turn
        "user_a_health": 100,
        "user_b_health": 100,
        "user_a_boost": False,  # No active boost
        "user_b_boost": False,
        "user_a_special_move": 0,
        "user_b_special_move": 0
    }
    return f"Battle started! @User{user_a} vs @User{user_b}\nFirst move is @User{user_a}'s!"
    
def handle_turn(user_id, action):
    """Handle the player's turn during the battle."""
    if user_id not in active_battles:
        return "You are not in a battle."
    
    battle = active_battles[user_id]
    
    # Check if it's the user's turn
    if battle["turn"] != user_id:
        return "It's not your turn!"
    
    opponent_id = battle["opponent"]
    
    # Randomize damage for attack
    damage = random.randint(10, 35)
    
    if action == "attack":
        # Deduct health from the opponent
        if user_id == battle["user_a"]:
            battle["user_b_health"] = deduct_health(opponent_id, damage)
        else:
            battle["user_a_health"] = deduct_health(opponent_id, damage)

    # If both players are still alive, switch turns
    if battle["user_a_health"] > 0 and battle["user_b_health"] > 0:
        battle["turn"] = opponent_id
        return f"@User{user_id} attacked! The opponent lost {damage} health.\nYour turn next!"
    
    # Determine winner and reward
    if battle["user_a_health"] <= 0:
        winner = opponent_id
    else:
        winner = user_id

    # Battle result (add random points and exp)
    points = random.randint(200, 300)
    exp = random.randint(0, 100)
    
    update_points(winner, points)
    # Simulate leveling up here (example)
    update_level(winner, points, exp)  

    return f"Battle over! @User{winner} wins!\nYou earned {points} points and {exp} EXP!"
