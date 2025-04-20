from telegram import ReplyKeyboardMarkup

def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["👤 Профиль", "⚔️ Сразиться с монстром"],
        ["🛒 Магазин", "📜 Квесты"]
    ], resize_keyboard=True)