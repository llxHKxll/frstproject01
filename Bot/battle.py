from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from random import randint
import time
from database.db_manager import update_points, update_user_data

active_battles = {}  # To track ongoing battles (format: {user_id: opponent_id})

def start_battle(client, message, challenger_id, opponent_id):
    """Start a new battle if both players are available."""
    if challenger_id in active_battles or opponent_id in active_battles:
        opponent_in_battle = active_battles.get(opponent_id)
        message.reply(
            f"@{message.reply_to_message.from_user.username} is already in a battle. Please wait for their battle to finish."
        )
        return

    # Initialize battle data
    active_battles[challenger_id] = opponent_id
    active_battles[opponent_id] = challenger_id

    battle_data = {
        "challenger": {
            "id": challenger_id,
            "username": message.from_user.username,
            "health": 100,
            "last_special_move_time": 0,
        },
        "opponent": {
            "id": opponent_id,
            "username": message.reply_to_message.from_user.username,
            "health": 100,
            "last_special_move_time": 0,
        },
        "turn": challenger_id,  # Start with the challenger
    }

    # Send battle start message
    battle_text = (
        f"🔥 **Battle Started!** 🔥\n\n"
        f"@{battle_data['challenger']['username']} vs. @{battle_data['opponent']['username']}\n"
        f"Both players start with 100 HP.\n\n"
        f"@{battle_data['challenger']['username']}, it's your turn! Choose your move:"
    )
    buttons = get_action_buttons()
    message.reply_text(battle_text, reply_markup=InlineKeyboardMarkup(buttons))

    return battle_data


def get_action_buttons():
    """Generate inline buttons for actions."""
    return [
        [
            InlineKeyboardButton("Attack", callback_data="battle_action_attack"),
            InlineKeyboardButton("Defend", callback_data="battle_action_defend"),
            InlineKeyboardButton("Special Move", callback_data="battle_action_special"),
        ]
    ]


def handle_battle_action(client, callback_query):
    """Handle a player's battle action."""
    data = callback_query.data.split("_")[-1]
    user_id = callback_query.from_user.id

    # Find battle
    opponent_id = active_battles.get(user_id)
    if not opponent_id:
        callback_query.answer("You're not in a battle!")
        return

    # Fetch battle data
    battle_data = get_battle_data(user_id)
    if not battle_data:
        callback_query.answer("Error fetching battle data.")
        return

    # Check turn
    if battle_data["turn"] != user_id:
        callback_query.answer("It's not your turn!")
        return

    # Process action
    opponent = "challenger" if battle_data["opponent"]["id"] == user_id else "opponent"
    player = "challenger" if battle_data["challenger"]["id"] == user_id else "opponent"
    action_text = ""

    if data == "attack":
        damage = randint(10, 35)
        battle_data[opponent]["health"] -= damage
        action_text = f"@{battle_data[player]['username']} attacked @{battle_data[opponent]['username']} for {damage} HP!"
    elif data == "defend":
        damage = randint(5, 15)
        battle_data[opponent]["health"] -= damage
        action_text = f"@{battle_data[player]['username']} defended, reducing damage to {damage} HP!"
    elif data == "special":
        current_time = time.time()
        last_special_time = battle_data[player]["last_special_move_time"]

        # Check cooldown for special move
        if current_time - last_special_time < 15:
            cooldown_remaining = 15 - int(current_time - last_special_time)
            callback_query.answer(f"Special Move is on cooldown. Wait {cooldown_remaining} seconds.")
            return

        damage = randint(25, 50)
        battle_data[opponent]["health"] -= damage
        battle_data[player]["last_special_move_time"] = current_time
        action_text = f"@{battle_data[player]['username']} used a special move for {damage} HP damage!"

    # Check for winner
    if battle_data[opponent]["health"] <= 0:
        reward_winner(callback_query, battle_data, player)
        end_battle(battle_data)
        return

    # Update turn and send action result
    battle_data["turn"] = battle_data[opponent]["id"]
    callback_query.message.edit_text(
        f"{action_text}\n\n"
        f"@{battle_data[opponent]['username']}, it's your turn! Choose your move:",
        reply_markup=InlineKeyboardMarkup(get_action_buttons()),
    )


def reward_winner(callback_query, battle_data, winner):
    """Reward the winning player with points and experience."""
    winner_data = battle_data[winner]
    points_reward = randint(200, 300)
    exp_reward = randint(20, 100)

    # Update database for the winner
    update_points(winner_data["id"], points_reward)
    update_user_data(winner_data["id"], new_exp=exp_reward, new_level=None)

    # Announce winner and rewards
    callback_query.message.reply_text(
        f"🎉 **{winner_data['username']} wins the battle!** 🎉\n\n"
        f"🏆 **Rewards:**\n"
        f"- {points_reward} Points\n"
        f"- {exp_reward} EXP"
    )


def get_battle_data(user_id):
    """Retrieve the battle data for a user."""
    opponent_id = active_battles.get(user_id)
    if not opponent_id:
        return None
    return {
        "challenger": {"id": user_id, "username": "Challenger", "health": 100, "last_special_move_time": 0},
        "opponent": {"id": opponent_id, "username": "Opponent", "health": 100, "last_special_move_time": 0},
        "turn": user_id,
    }


def end_battle(battle_data):
    """End a battle and remove it from active battles."""
    challenger_id = battle_data["challenger"]["id"]
    opponent_id = battle_data["opponent"]["id"]

    active_battles.pop(challenger_id, None)
    active_battles.pop(opponent_id, None)
