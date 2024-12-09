import random
from database.db_manager import update_points

# In-memory storage for active games
active_games = {}  # Format: {user_id: {"number": int, "attempts": int, "difficulty": str}}

DIFFICULTY_SETTINGS = {
    "easy": {"range": (1, 50), "attempts": 10, "prize": 10},
    "medium": {"range": (1, 100), "attempts": 8, "prize": 30},
    "hard": {"range": (1, 200), "attempts": 5, "prize": 50},
}

def start_game(user_id, difficulty):
    """Start a new guess game for the user with a specific difficulty."""
    if difficulty not in DIFFICULTY_SETTINGS:
        return "Invalid difficulty. Please choose from: easy, medium, hard."

    settings = DIFFICULTY_SETTINGS[difficulty]
    number = random.randint(*settings["range"])  # Generate a random number based on range
    active_games[user_id] = {
        "number": number,
        "attempts": settings["attempts"],
        "difficulty": difficulty,
    }
    return f"🎮 **Guess the Number Game Started!** 🎮\n" \
           f"I'm thinking of a number between {settings['range'][0]} and {settings['range'][1]}.\n" \
           f"You have {settings['attempts']} attempts to guess it. Use /guess <number> to make a guess!"

def process_guess(user_id, guess):
    """Process a user's guess."""
    if user_id not in active_games:
        return "You don't have an active game. Use /start_guess <difficulty> to start a new game."

    game = active_games[user_id]

    # Check attempts
    if game["attempts"] <= 0:
        correct_number = game["number"]
        del active_games[user_id]
        return f"You've run out of attempts! The correct number was {correct_number}.\nUse /start_guess <difficulty> to play again."

    # Process the guess
    game["attempts"] -= 1
    if guess == game["number"]:
        prize = DIFFICULTY_SETTINGS[game["difficulty"]]["prize"]
        del active_games[user_id]  # Clear the game for this user
        update_points(user_id, prize)  # Reward points based on difficulty
        return f"🎉 **Congratulations! You guessed the number correctly!** 🎉\n" \
               f"You've earned {prize} points! Use /start_guess <difficulty> to play again."
    elif guess < game["number"]:
        return f"🔽 Too Low! You have {game['attempts']} attempts left."
    else:
        return f"🔼 Too High! You have {game['attempts']} attempts left."
