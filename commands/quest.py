from telegram import Update
from telegram.ext import (
    ContextTypes
)
from gui.keyboards import main_menu_keyboard

async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ЕЩЕ НЕ РАБОТАЕТ",
        reply_markup=main_menu_keyboard()
    )