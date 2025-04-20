# bot/handlers/profile_handler.py

import requests
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "http://127.0.0.1:9000"

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)

    response = requests.post(f"{API_URL}/profile", json={"tg_id": tg_id}).json()
    await update.message.reply_text(
        response.get("message", "Ошибка при получении профиля"),
        parse_mode="Markdown"
    )
