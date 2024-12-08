import sqlite3
import os

# Ensure the 'database' directory exists
database_dir = os.path.join(os.path.dirname(__file__), 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# Correct path to the SQLite database
DB_PATH = os.path.join(database_dir, "user_data.db")

def connect_db():
    """Connect to the SQLite database."""
    print(f"Connecting to database at: {DB_PATH}")  # This will print the connection log
    return sqlite3.connect(DB_PATH)

# In db_manager.py - Modify the `create_db()` function to add this column
def create_db():
    """Initialize the database by creating tables."""
    with connect_db() as conn:
        c = conn.cursor()
        # Corrected SQL query to include the new column xp_booster_expiry
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                points INTEGER DEFAULT 10000,
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                health INTEGER DEFAULT 100,
                last_activity_time INTEGER DEFAULT 0,
                last_claimed INTEGER DEFAULT 0,
                chat_id INTEGER DEFAULT 0,
                xp_booster_expiry INTEGER DEFAULT 0  -- Add this column to track booster expiry
            )
        ''')  
        conn.commit()

def add_user(user_id, username=None):
    """Add a new user to the database."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, points, level, exp, health, last_activity_time, last_claimed, chat_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, username or "Unknown", 10000, 1, 0, 100, 0, 0, chat_id)  # Add last_claimed as 0
        )
        conn.commit()
        print(f"Added user: {user_id}, {username}")  # Debugging line

def get_user(user_id):
    """Retrieve user data from the database."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, username, points, level, exp, health, last_activity_time, last_claimed, xp_booster_expiry
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return cursor.fetchone()  # Include xp_booster_expiry in the results
        
def update_points(user_id, points):
    """Update user points."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET points = points + ?
            WHERE user_id = ?
            """,
            (points, user_id),
        )
        conn.commit()

def update_level(user_id, level, exp):
    """Update user level and experience."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET level = ?, exp = ?
            WHERE user_id = ?
            """,
            (level, exp, user_id),
        )
        conn.commit()

def update_health(user_id, health):
    """Update user health points."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET health = ?
            WHERE user_id = ?
            """,
            (health, user_id),
        )
        conn.commit()

def update_user_data(user_id, new_exp, new_level):
    """Update user experience and level."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET exp = ?, level = ?
            WHERE user_id = ?
            """,
            (new_exp, new_level, user_id),
        )
        conn.commit()

def ensure_user_exists(user_id, username=None):
    """Ensure the user exists in the database. If not, add them."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE user_id = ?",
            (user_id,),
        )
        if cursor.fetchone() is None:  # User doesn't exist
            cursor.execute(
                """
                INSERT INTO users (user_id, username)
                VALUES (?, ?)
                """,
                (user_id, username or "Unknown"),
            )
            conn.commit()

def get_group_members(chat_id, order_by="points"):
    """Fetch members in the group sorted by points or level."""
    valid_columns = ["points", "level"]
    if order_by not in valid_columns:
        order_by = "points"  # Default to points if invalid column
    
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT username, {order_by}
            FROM users
            WHERE chat_id = ?
            ORDER BY {order_by} DESC
        """, (chat_id,))
        return cursor.fetchall()  # Returns a list of tuples (username, points/level)
