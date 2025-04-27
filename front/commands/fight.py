# bot/handlers/fight_handler.py

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

API_URL = os.getenv("BACKEND_URL", "http://backend:9000")

def build_fight_keyboard(actions: list, items=None, skills=None):
    keyboard = []

    if "attack" in actions:
        keyboard.append([InlineKeyboardButton("⚔️ Атаковать", callback_data="fight_attack")])

    if items:
        for item in items[:3]:  # максимум 3 предмета
            btn = InlineKeyboardButton(
                f"🎒 {item['name']} ({item['count']})",
                callback_data=f"fight_useitem_{item['id']}"
            )
            keyboard.append([btn])

    if skills:
        for skill in skills[:3]:  # максимум 3 навыка
            btn = InlineKeyboardButton(
                f"🔮 {skill['name']} (🔵{skill['mana_cost']})",
                callback_data=f"fight_useskill_{skill['id']}"
            )
            keyboard.append([btn])

    if "flee" in actions:
        keyboard.append([InlineKeyboardButton("🏃 Бежать", callback_data="fight_flee")])

    return InlineKeyboardMarkup(keyboard)


async def fight_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    response = requests.post(f"{API_URL}/fight/start", json={"tg_id": tg_id}).json()

    if "error" in response:
        await update.message.reply_text(response["error"])
        return

    msg = response["message"]
    fight = response.get("fight", {})

    msg += (
        f"\n❤️ HP: {fight.get('user_hp')}/{context.user_data.get('max_hp', '?')}"
        f"\n🔮 Mana: {fight.get('user_mana', '?')}"
        f"\n💥 Противник: {fight.get('monster_name')} ({fight.get('monster_hp')} HP)"
    )

    context.user_data["max_hp"] = fight.get("user_hp")  # сохраняем для отображения

    await update.message.reply_text(
        msg,
        reply_markup=build_fight_keyboard(
            response.get("actions", []),
            response.get("items"),
            response.get("skills")
        )
    )

async def fight_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_id = str(query.from_user.id)

    action = query.data.replace("fight_", "")
    action = query.data.replace("fight_", "")
    data = {"tg_id": tg_id}

    if action.startswith("useskill_"):
        data["action"] = "useskill"
        data["skill_id"] = int(action.split("_")[1])
    elif action.startswith("useitem_"):
        data["action"] = "useitem"
        data["item_id"] = int(action.split("_")[1])
    else:
        data["action"] = action
    response = requests.post(f"{API_URL}/fight/action", json=data).json()

    msg = response.get("message", "Ошибка")

    if "fight" in response:
        fight = response["fight"]
        msg += (
            f"\n❤️ HP: {fight.get('user_hp')}/{context.user_data.get('max_hp', '?')}"
            f"\n🔮 Mana: {fight.get('user_mana', '?')}"
            f"\n💥 Противник: {fight.get('monster_name')} ({fight.get('monster_hp')} HP)"
            f"\nРаунд: {fight.get('round')}"
        )

    await query.edit_message_text(
        text=msg,
        reply_markup=build_fight_keyboard(
            response.get("actions", []),
            response.get("items"),
            response.get("skills")
        ) if "actions" in response else None
    )
