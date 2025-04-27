import logging
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)
from commands.quest import quest_command, quest_callback
from commands.start import start, button_callback
from commands.userProfile import profile_command
from commands.shop import buy_callback, shop_command
from commands.fight import fight_command, fight_callback
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
    application.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile_command))
    application.add_handler(MessageHandler(filters.Regex("⚔️ Сразиться с монстром"), fight_command))
    application.add_handler(MessageHandler(filters.Regex("🛒 Магазин"), shop_command))
    #application.add_handler(MessageHandler(filters.Regex("📜 Квесты"), quest))
    application.add_handler(CallbackQueryHandler(fight_callback, pattern="^fight_"))
    application.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy"))
    application.add_handler(MessageHandler(filters.Regex("📜 Квесты"), quest_command))
    application.add_handler(CallbackQueryHandler(quest_callback, pattern="^(current_quest|cancel_quest|accept_quest_|back_to_quests)"))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()