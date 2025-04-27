import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from gui.keyboards import main_menu_keyboard
import os

API_URL = os.getenv("BACKEND_URL", "http://backend:9000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    username = update.effective_user.username or "user"
    response = requests.post(f"{API_URL}/start", json={
        "tg_id": tg_id,
        "username": username
    }).json()

    if "classes" in response:
        buttons = [
            [InlineKeyboardButton("Маг", callback_data="class_mage")],
            [InlineKeyboardButton("Воин", callback_data="class_warrior")],
            [InlineKeyboardButton("Лучник", callback_data="class_archer")]
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(response["message"], reply_markup=markup)
    else:
        k = main_menu_keyboard()
        await update.message.reply_text(response.get("message", "Ошибка"), reply_markup=k)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tg_id = str(query.from_user.id)
    username = str(query.from_user.username)
    chosen = query.data.replace("class_", "")

    response = requests.post(f"{API_URL}/start/class", json={
        "tg_id": tg_id,
        "chosen": chosen,
        "username": username
    }).json()
    
    k = main_menu_keyboard()

    await query.edit_message_text(response.get("message", "Ошибка"), reply_markup=k)
