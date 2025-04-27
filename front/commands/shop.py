# bot/handlers/shop_handler.py

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

API_URL = os.getenv("BACKEND_URL", "http://backend:9000")

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    response = requests.post(f"{API_URL}/shop/items", json={"tg_id": tg_id}).json()

    if "error" in response:
        await update.message.reply_text(response["error"])
        return

    keyboard = []
    print(response["items"])
    for item in response["items"]:
        keyboard.append([
            InlineKeyboardButton(
                f"{item['name']} - {item['price']}💰",
                callback_data=f"buy_{item['id']}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"{response['message']}\nВаше золото: {response['user_gold']}💰",
        reply_markup=reply_markup
    )

async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tg_id = str(query.from_user.id)
    item_id = int(query.data.split("_")[1])
    
    print(tg_id, item_id)

    response = requests.post(f"{API_URL}/shop/buy", json={
        "tg_id": tg_id,
        "item_id": item_id
    }).json()

    await query.edit_message_text(
        text=response.get("message", "Ошибка")
    )
