import logging
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)
from commands.start import start, button_callback
from commands.profile import profile
from commands.shop import buy_item, shop
from commands.fight import fight, fight_action
from commands.quest import *
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile))
    application.add_handler(MessageHandler(filters.Regex("⚔️ Сразиться с монстром"), fight))
    application.add_handler(MessageHandler(filters.Regex("🛒 Магазин"), shop))
    #application.add_handler(MessageHandler(filters.Regex("📜 Квесты"), quest))
    application.add_handler(CallbackQueryHandler(fight_action, pattern="^fight_"))
    application.add_handler(CallbackQueryHandler(buy_item, pattern="^buy"))
    
    application.add_handler(MessageHandler(filters.Regex("📜 Квесты"), quest))
    application.add_handler(CallbackQueryHandler(handle_quest_action, pattern="^(current_quest|cancel_quest|accept_quest_|back_to_quests)"))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()