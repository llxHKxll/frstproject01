from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time

# Example shop items
SHOP_ITEMS = {
    1: {
        "name": "2x XP Booster (24 Hours)",
        "price": 300,
        "description": "Boost your XP gain for 24 hours.",
        "condition": "no_active_booster",
    },
    2: {
        "name": "Health Refill",
        "price": 20,
        "description": "Instantly restore health to 100%.",
        "condition": "not_full_health",
    }
}

# Navigation settings
ITEMS_PER_PAGE = 6

# Placeholder user data (replace with database functions)
USER_DATA = {
    123456789: {  # Replace with actual user ID
        "coins": 500,
        "health": 75,
        "xp_booster_active": False,
    }
}

def get_shop_page(page_number):
    """Generate the shop text and inline buttons for a given page."""
    start_index = (page_number - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    items = list(SHOP_ITEMS.items())[start_index:end_index]
    
    if not items:
        return "No items available on this page.", InlineKeyboardMarkup([])

    # Generate shop text
    shop_text = "🛒 **Welcome to the Shop!** 🛒\n\n"
    for item_id, item in items:
        shop_text += f"{item_id}. **{item['name']}** - {item['price']} coins\n"
        shop_text += f"   {item['description']}\n\n"

    # Generate inline buttons
    buttons = [
        [InlineKeyboardButton(item["name"], callback_data=f"buy_{item_id}")]
        for item_id, item in items
    ]

    # Add navigation buttons
    if len(SHOP_ITEMS) > ITEMS_PER_PAGE:
        nav_buttons = []
        if start_index > 0:
            nav_buttons.append(InlineKeyboardButton("Previous", callback_data=f"shop_page_{page_number - 1}"))
        if end_index < len(SHOP_ITEMS):
            nav_buttons.append(InlineKeyboardButton("Next", callback_data=f"shop_page_{page_number + 1}"))
        buttons.append(nav_buttons)

    return shop_text, InlineKeyboardMarkup(buttons)

def handle_purchase(user_id, item_id):
    """Handle the purchase of a shop item."""
    user = USER_DATA.get(user_id)
    if not user:
        return "User not found."

    item = SHOP_ITEMS.get(item_id)
    if not item:
        return "Item not found."

    # Check conditions
    if item["condition"] == "no_active_booster" and user["xp_booster_active"]:
        return "You already have an active XP Booster. Wait for it to expire before purchasing another."
    if item["condition"] == "not_full_health" and user["health"] == 100:
        return "Your health is already full. You don't need a Health Refill."

    # Check coins
    if user["coins"] < item["price"]:
        return "You don't have enough coins to buy this item."

    # Deduct coins and apply the effect
    user["coins"] -= item["price"]
    if item["condition"] == "no_active_booster":
        user["xp_booster_active"] = True
        # Add logic to expire the booster after 24 hours (not implemented here)
    if item["condition"] == "not_full_health":
        user["health"] = 100

    return f"You successfully purchased: {item['name']}!"
