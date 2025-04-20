# bot/handlers/quest_handler.py

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

API_URL = "http://127.0.0.1:9000"

async def quest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    response = requests.post(f"{API_URL}/quest", json={"tg_id": tg_id, "action": "list"}).json()

    if "quests" in response:
        buttons = []
        for quest in response["quests"]:
            buttons.append([
                InlineKeyboardButton(
                    f"{quest['name']} (Ур. {quest['level']})",
                    callback_data=f"accept_quest_{quest['id']}"
                )
            ])
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(response["message"], reply_markup=markup)
    else:
        await update.message.reply_text(response.get("message", "Ошибка"))

async def quest_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_id = str(query.from_user.id)

    data = query.data
    if data == "current_quest":
        action = "current"
    elif data == "cancel_quest":
        action = "cancel"
    elif data.startswith("accept_quest_"):
        action = "accept"
        quest_id = int(data.split("_")[2])
    else:
        await query.edit_message_text("Неверное действие.")
        return

    payload = {"tg_id": tg_id, "action": action}
    if action == "accept":
        payload["quest_id"] = quest_id

    response = requests.post(f"{API_URL}/quest", json=payload).json()
    await query.edit_message_text(response.get("message", "Ошибка"))
