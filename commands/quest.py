import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes
)
from sqlalchemy.orm.attributes import flag_modified
from db.db import Item, User, Quest, Monster
from db.dbSession import session
from gui.keyboards import main_menu_keyboard

async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()
    
    if not user:
        await update.message.reply_text("Сначала создайте персонажа!")
        return

    keyboard = []

    # Если есть активный квест
    if user.active_quest_id:
        quest = session.query(Quest).get(user.active_quest_id)
        keyboard.append([InlineKeyboardButton("📌 Текущий квест", callback_data="current_quest")])
        keyboard.append([InlineKeyboardButton("❌ Отменить квест", callback_data="cancel_quest")])
    else:
        # Получаем доступные квесты для уровня игрока
        available_quests = session.query(Quest).filter(
            Quest.min_level <= user.level,
            ~Quest.quest_id.in_(user.completed_quests)
        ).limit(3).all()
        
        for quest in available_quests:
            keyboard.append([InlineKeyboardButton(
                f"{quest.name} (Ур. {quest.min_level})", 
                callback_data=f"accept_quest_{quest.quest_id}"
            )])
    
    #keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    
    await update.message.reply_text(
        "📜 Доска квестов:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    
async def handle_quest_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("1")
    query = update.callback_query
    print("2")
    await query.answer()
    print("3")
    data = query.data
    print("4")
    
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()
    if not user:
        return

    if data == "current_quest":
        quest = session.query(Quest).get(user.active_quest_id)
        progress = get_quest_progress(user, quest)
        await query.edit_message_text(
            f"📌 Активный квест: {quest.name}\n"
            f"▸ {quest.description}\n"
            f"Прогресс: {progress}/{quest.required}\n"
            f"Награда: {quest.reward_gold}💰 + {quest.reward_xp} XP",
            #reply_markup=InlineKeyboardMarkup([
            #    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_quests")]
            #])
        )
    
    elif data == "cancel_quest":
        user.active_quest_id = None
        user.quest_progress = 0
        session.commit()
        await query.edit_message_text(
            "Квест отменён!",
            #reply_markup=InlineKeyboardMarkup([
            #    [InlineKeyboardButton("📜 К списку квестов", callback_data="back_to_quests")]
            #])
        )
    
    elif data.startswith("accept_quest_"):
        print("TESTSETSET")
        quest_id = int(data.split("_")[2])
        print(quest_id)
        user.active_quest_id = quest_id
        print(user.active_quest_id)
        user.quest_progress = 0
        print(user.quest_progress)
        session.commit()
        await query.edit_message_text(
            text="🎉 Квест принят! Проверьте прогресс в профиле.",
            #reply_markup=InlineKeyboardMarkup([
            #    [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
            #    [InlineKeyboardButton("📜 К квестам", callback_data="quest")]
            #])
        )

def get_quest_progress(user, quest):
    """Вычисляет текущий прогресс квеста"""
    if quest.quest_type == "kill":
        # В вашем бою нужно увеличивать счетчик убийств нужных монстров
        return user.quest_progress
    elif quest.quest_type == "collect":
        # Проверяем количество предметов в инвентаре
        return user.inventory.get(str(quest.target), 0)
    return user.quest_progress

def check_quest_completion(user):
    """Проверяет завершение квеста и выдает награды"""
    if not user.active_quest_id:
        return False
    
    quest = session.query(Quest).get(user.active_quest_id)
    progress = get_quest_progress(user, quest)
    
    if progress >= quest.required:
        # Выдаем награду
        user.gold += quest.reward_gold
        user.xp += quest.reward_xp
        if quest.reward_item_id:
            user.inventory[str(quest.reward_item_id)] = user.inventory.get(str(quest.reward_item_id), 0) + 1
            flag_modified(user, "inventory")
        
        # Добавляем квест в завершенные
        if not user.completed_quests:
            user.completed_quests = []
        user.completed_quests.append(quest.quest_id)
        flag_modified(user, "completed_quests")
        
        # Сбрасываем активный квест
        user.active_quest_id = None
        user.quest_progress = 0
        session.commit()
        
        return True
    return False

'''# В обработчике боя добавьте проверку квестов на убийство монстров
async def fight_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... существующий код ...
    
    # Проверка квеста после победы
    if fight_context['monster_hp'] <= 0:
        user = session.query(User).filter_by(tg_id=u_tg_id).first()
        if user.active_quest_id:
            quest = session.query(Quest).get(user.active_quest_id)
            if quest.quest_type == "kill" and str(quest.target) == str(monster.id):
                user.quest_progress += 1
                session.commit()
                if check_quest_completion(user):
                    await query.edit_message_text(
                        text=f"{result_message}\n\n🎉 Вы выполнили квест {quest.name}!\n"
                             f"Получено: {quest.reward_gold}💰 и {quest.reward_xp} XP",
                    )
                    return

'''