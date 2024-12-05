import sys
import os
from flask import Flask
from threading import Thread
from Bot.main import app  # Import your Pyrogram bot

# Flask app to satisfy Render's port binding requirement
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    """Run the Flask server on the assigned Render port."""
    port = int(os.environ.get("PORT", 5000))  # Render provides the PORT environment variable
    flask_app.run(host="0.0.0.0", port=port)

def run_bot():
    """Run the Telegram bot."""
    app.run()

if __name__ == "__main__":
    # Run Flask and the bot in separate threads
    Thread(target=run_flask).start()
    run_bot()
