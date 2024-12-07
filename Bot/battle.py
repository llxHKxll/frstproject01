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
    
@app.on_callback_query(filters.regex(r"battle_turn_(\d+)_(\w+)"))
def battle_turn(client, callback_query):
    """Handle the player's turn during the battle."""
    user_id = callback_query.from_user.id
    battle = active_battles.get(user_id)
    
    if not battle:
        callback_query.answer("You are not in a battle.")
        return

    # Check if it's the user's turn
    if battle["turn"] != user_id:
        callback_query.answer("It's not your turn!")
        return
    
    # Action selected (attack, defend, special move)
    action = callback_query.data.split("_")[-1]
    damage = random.randint(10, 35)  # Damage range

    if action == "attack":
        # Apply damage to the opponent
        opponent_id = battle["opponent"]
        if user_id == battle["user_a"]:
            battle["user_b_health"] -= damage
        else:
            battle["user_a_health"] -= damage

        # Switch turns after the action
        battle["turn"] = opponent_id
        callback_query.answer(f"@User{user_id} attacked! Opponent lost {damage} health.\nYour turn next!")

    elif action == "defend":
        # Implement defense logic (reduce damage taken by 50% or other mechanics)
        callback_query.answer(f"@User{user_id} defended!")
    
    elif action == "special":
        # Implement special move (larger damage or special effects)
        special_damage = random.randint(20, 50)
        opponent_id = battle["opponent"]
        if user_id == battle["user_a"]:
            battle["user_b_health"] -= special_damage
        else:
            battle["user_a_health"] -= special_damage
        
        callback_query.answer(f"@User{user_id} used a special move! Opponent lost {special_damage} health.")

    # Check if the battle is over
    if battle["user_a_health"] <= 0 or battle["user_b_health"] <= 0:
        winner = user_id if battle["user_a_health"] > 0 else battle["opponent"]
        points = random.randint(200, 300)
        exp = random.randint(0, 100)
        
        update_points(winner, points)
        update_level(winner, points, exp)

        # End the battle
        active_battles.pop(user_id, None)
        active_battles.pop(battle["opponent"], None)
        callback_query.answer(f"Battle over! @User{winner} wins!\nYou earned {points} points and {exp} EXP!")
        return

    # If the battle is ongoing, continue switching turns
    opponent_id = battle["opponent"]
    battle["turn"] = opponent_id
    callback_query.answer(f"Now it's @User{opponent_id}'s turn!")

    def show_battle_buttons(user_id):
    """Generate inline buttons for battle actions."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Attack", callback_data=f"battle_turn_{user_id}_attack")],
        [InlineKeyboardButton("Defend", callback_data=f"battle_turn_{user_id}_defend")],
        [InlineKeyboardButton("Special Move", callback_data=f"battle_turn_{user_id}_special")]
    ])
