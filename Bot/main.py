import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Bot.flood_control import check_flood
from Bot.leveling import level_up
from database.db_manager import create_db, add_user, ensure_user_exists, get_user, update_points, update_level, update_health, update_user_data, connect_db

API_ID = "21989020"
API_HASH = "3959305ae244126404702aa5068ba15c"
BOT_TOKEN = "8141351816:AAG1_YB0l88X0SLAHnos9iODdZuCdNEfuFo"

app = Client(
  name="pyxn",
  api_id=API_ID,
  api_hash=API_HASH,
  bot_token=BOT_TOKEN
)

# Create DB on bot startup
create_db()

@app.on_message(filters.command("start"))
def start_handler(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name  # Use first name for the link
    username = message.from_user.username or first_name

    # Ensure user exists in the database
    ensure_user_exists(user_id, username)

    # Fetch user data from the database
    user_data = get_user(user_id)
    if user_data:
        user_id, username, points, level, exp, health, last_activity_time, last_claimed = user_data

      # Create a user link using the user's first name
        user_link = f'<a href="tg://user?id={user_id}">{first_name}</a>'

      # Inline keyboard with a button to your chat group
        chat_group_url = "https://t.me/KaisenWorld"  # Replace with your group link
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Join Chat Group", url=chat_group_url)]
            ]
        )

        # Send a welcome message with user data and the user link
        message.reply_photo(
            photo="https://imgur.com/a/hJU9sB4",
            caption=(
                f"Hey {user_link}, 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝗍𝗁𝖾 𝖯𝗒𝗑𝗇 𝖡𝗈𝗍 ! 🎉\n\n"
                f"<b>📜 ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴛᴏᴋᴇɴs ?</b>\n"
                f"- ᴊᴜsᴛ ᴄʜᴀᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ! ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ sᴇɴᴅ ɢᴇᴛs ʏᴏᴜ ᴄʟᴏsᴇʀ ᴛᴏ ᴇᴀʀɴɪɴɢ ᴋᴀɪᴢᴇɴ ᴛᴏᴋᴇɴs.\n\n"
                f"𝖦𝖾𝗍 𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝗇𝗈𝗐 ! 𝗍𝗒𝗉𝖾 /help 𝖿𝗈𝗋 𝗆𝗈𝗋𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.\n\n"
                f"🎯 **ʏᴏᴜʀ sᴛᴀᴛs :**\n• ᴘᴏɪɴᴛs : {points}\n• ʟᴇᴠᴇʟ : {level}"
            ),
          reply_markup=keyboard,  # Attach the keyboard to the message
        )

    # If user data doesn't exist, add the user and fetch data again
    if user_data is None:
        add_user(user_id, username)
        user_data = get_user(user_id)


@app.on_message(filters.command("profile"))
def profile_handler(client, message):
    # Check if the command is replied to a message or tagged with @username
    if message.reply_to_message:
        # If the command is used by replying to another user's message
        target_user = message.reply_to_message.from_user
    elif message.entities and message.entities[0].type == "mention":
        # If the command is used by tagging a user (e.g., @username)
        target_user = message.entities[0].user
    else:
        # If no reply or mention, show the profile of the user who sent the command
        target_user = message.from_user

    # Check if the target is a bot
    if target_user.is_bot:
        message.reply("You can't get the profile of a bot.")
        return

    # Fetch user data from the database for the target user
    user_data = get_user(target_user.id)
    if user_data:
        user_id, username, points, level, exp, health, last_activity_time, last_claimed = user_data
        # Create a user link using the user's first name
        user_link = f'<a href="tg://user?id={target_user.id}">{target_user.first_name}</a>'
        
        # Send the profile details
        message.reply_text(
            f"**{user_link}'s Profile :**\n"
            f"Points: {points}\n"
            f"Level: {level}\n"
            f"EXP: {exp}\n"
            f"Health: {health}"
        )
    else:
        message.reply_text(f"Error fetching {target_user.first_name}'s profile. Please try again later or try after using /start !")

      
@app.on_message(filters.text)
def handle_message(client, message):
  # List of allowed group chat IDs (replace with your actual group IDs)
    ALLOWED_GROUPS = [-1002135192853, -1002324159284]  # Add your group IDs here

    # Ensure the message is from an allowed group
    if message.chat.id not in ALLOWED_GROUPS:
        return  # Ignore messages outside allowed groups

    user_id = message.from_user.id

    # Flood control logic
    if check_flood(user_id):
        message.reply("You are sending messages too quickly. Please wait a few seconds.")
    else:
        # Increment experience and level
        level_up(user_id, message.text) 

# Daily reward amount
DAILY_REWARD = 100

@app.on_message(filters.command("daily"))
def daily_reward(client, message):
    user_id = message.from_user.id
    
    # Fetch user data
    user_data = get_user(user_id)
    if not user_data:
        message.reply("Error: User not found in the database.")
        return

    user_id, username, points, level, exp, health, last_activity_time, last_claimed = user_data
    
    # Get the current time
    current_time = time.time()  # Get current time in seconds

    # Check if the user has already claimed their daily reward
    if last_claimed != 0:
        # Calculate the time difference between now and last claim
        time_difference = current_time - last_claimed

        # If less than 24 hours, the user can't claim again
        if time_difference < 86400:  # 86400 seconds = 24 hours
            remaining_time = 86400 - time_difference  # Time left to claim
            remaining_hours = remaining_time // 3600
            remaining_minutes = (remaining_time % 3600) // 60
            message.reply(f"You've already claimed your reward. Please wait {int(remaining_hours)} hours and {int(remaining_minutes)} minutes to claim again.")
            return

    # Give the user their daily reward
    new_points = points + DAILY_REWARD

    # Update the user's points and last claim time
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET points = ?, last_claimed = ?
            WHERE user_id = ?
            """,
            (new_points, current_time, user_id)
        )
        conn.commit()

    # Inform the user that they've successfully claimed their reward
    message.reply(f"🎉 You've successfully claimed your daily reward of {DAILY_REWARD} points! Your new point balance is {new_points}.")

if __name__ == "__main__":
    app.run()
