import json
import logging
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from db import Base, Item, User, Monster  # Импортируем модели из файла models.py

# Настройки подключения к базе данных
DATABASE_URI = 'postgresql+psycopg2://postgres:3259@localhost:5433/teamdev'

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URI)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

# Токен вашего бота
TOKEN = '8079560430:AAF66xiKN5P-POGt0geZOctpOPEWMcsmZlA'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

# Главное меню с кнопками
def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["👤 Профиль", "⚔️ Сразиться с монстром"],
        ["🛒 Магазин", "📜 Квесты"]
    ], resize_keyboard=True)

# Команда /start — создание персонажа
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_tg_id = str(update.effective_user.id)
    username = update.effective_user.username

    # Проверяем, есть ли пользователь в базе
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы уже создали персонажа!",
            reply_markup=main_menu_keyboard()
        )
    else:
        # Создаем меню выбора класса
        keyboard = [
            [InlineKeyboardButton("Маг", callback_data='class_mage')],
            [InlineKeyboardButton("Воин", callback_data='class_warrior')],
            [InlineKeyboardButton("Лучник", callback_data='class_archer')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите класс персонажа:",
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    u_tg_id = str(query.from_user.id)
    username = query.from_user.username

    # Определяем выбранный класс
    if query.data == 'class_mage':
        class_ = "Mage"
        health = 80
        mana = 100
        attack = 8
        defense = 3
        abilities = {"skill1": "Fireball"}
        inventory = {"item1": "Staff"}
    elif query.data == 'class_warrior':
        class_ = "Warrior"
        health = 100
        mana = 50
        attack = 10
        defense = 5
        abilities = {"skill1": "Slash"}
        inventory = {"item1": "Sword"}
    elif query.data == 'class_archer':
        class_ = "Archer"
        health = 90
        mana = 60
        attack = 12
        defense = 4
        abilities = {"skill1": "Arrow Shot"}
        inventory = {"item1": "Bow"}

    # Создаем нового персонажа
    new_user = User(
        tg_id=u_tg_id,
        username=username,
        class_=class_,
        level=1,
        xp=0,
        health=health,
        mana=mana,
        attack=attack,
        defense=defense,
        gold=0,
        energy=10,
        abilities=abilities,
        inventory=inventory
    )
    session.add(new_user)
    session.commit()
    
    await query.edit_message_text(
        text=f"Персонаж создан! Вы — {class_}.",
        reply_markup=None  # Убираем клавиатуру
    )

    # Отправляем главное меню
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_markup=main_menu_keyboard()
    )


# Команда /profile — просмотр профиля
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if not user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Сначала создайте персонажа с помощью /start.",
            reply_markup=main_menu_keyboard()
        )
        return

    # Получаем полную информацию о предметах из инвентаря
    inventory_items = user.inventory if isinstance(user.inventory, dict) else {}
    inventory_text = "📭 Пусто"
    
    if inventory_items:
        print(inventory_items)
        # Получаем данные о предметах из БД одним запросом
        item_ids = [int(item_id) for item_id in inventory_items.keys()]
        items = session.query(Item).filter(Item.item_id.in_(item_ids)).all() if item_ids else []
        
        # Создаем словарь для быстрого доступа
        items_dict = {str(item.item_id): item for item in items}
        
        # Формируем текст инвентаря
        inventory_lines = []
        for item_id, count in inventory_items.items():
            item = items_dict.get(item_id)
            if item:
                line = f"🔹 {item.name}: {count} шт."
                if item.attack_bonus > 0:
                    line += f" (+{item.attack_bonus}⚔)"
                if item.defense_bonus > 0:
                    line += f" (+{item.defense_bonus}🛡)"
                inventory_lines.append(line)
        
        inventory_text = "\n".join(inventory_lines) if inventory_lines else "📭 Пусто"

    # Формирование текста профиля
    profile_text = (
        f"👤 *Профиль {user.username}*\n"
        f"⚜️ Уровень: *{user.level}* (Опыт: {user.xp}/{user.level * 100 + 100})\n"
        f"🏅 Класс: *{user.class_}*\n\n"
        f"⚔️ Атака: *{user.attack}*  |  🛡 Защита: *{user.defense}*\n"
        f"❤️ Здоровье: *{user.health}*\n"
        f"🔮 Мана: *{user.mana}*\n"
        f"⚡ Энергия: *{user.energy}/10*\n"
        f"💰 Золото: *{user.gold}*\n\n"
        f"🎒 *Инвентарь ({len(inventory_items)} предметов)*:\n{inventory_text}"
    )

    # Добавляем прогресс-бар для энергии
    energy_bar = "LITENERG" #⚡[" + "█" * user.energy + "░" * (10 - user.energy) + "]"
    
    # Добавляем информацию о квестах, если есть
   # if user.active_quest:
    #    quest = session.query(Quest).get(user.active_quest)
     #   if quest:
      #      profile_text += f"\n\n📜 *Активный квест*: {quest.name}\n"
       #     profile_text += f"▸ {quest.description}\n"
        #    profile_text += f"Прогресс: {user.quest_progress}/{quest.required}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{profile_text}\n\n{energy_bar}",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )


def get_random_monster():
    """Возвращает случайного монстра (без привязки к сессии БД)"""
    monsters = session.query(Monster).all()
    monster = random.choice(monsters)
    # Создаем копию объекта, чтобы не изменять данные в БД
    from copy import deepcopy
    return deepcopy(monster)

# Команда /fight — битва с монстром
async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if not user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сначала создайте персонажа с помощью /start.",
            reply_markup=main_menu_keyboard()
        )
        return

    if user.energy <= 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="У вас закончилась энергия. Подождите, пока она восстановится.",
            reply_markup=main_menu_keyboard()
        )
        return

    # Мок-данные для навыков (замените на реальные из БД)
    mock_skills = [
        {"id": 1, "name": "Огненный шар", "mana_cost": 10, "type": "damage", "power": 15},
        {"id": 2, "name": "Лечение", "mana_cost": 8, "type": "heal", "power": 20},
        {"id": 3, "name": "Щит", "mana_cost": 5, "type": "buff_defense", "power": 7}
    ]

    # Получаем случайного монстра (временного, без сохранения в БД)
    monster = get_random_monster()
    current_round = 1
    monster_current_hp = monster.health
    user_current_hp = user.health
    user_current_mana = user.mana
    
        
        
    inventory_items = user.inventory if isinstance(user.inventory, dict) else {}
    
    if inventory_items:
        print(inventory_items)
        # Получаем данные о предметах из БД одним запросом
        item_ids = [int(item_id) for item_id in inventory_items.keys()]
        items = session.query(Item).filter(Item.item_id.in_(item_ids)).all() if item_ids else []
        
        # Создаем словарь для быстрого доступа
        items_dict = {str(item.item_id): item for item in items}
        
        # Формируем текст инвентаря
        inv = []
        for item_id, count in inventory_items.items():
            item = items_dict.get(item_id)
            if item:
                inv.append({
                    "id": item.item_id,
                    "name": item.name,
                    "type": item.type,
                    "count": count,
                    "power": item.power 
                })

    
    print(items_dict)
    print(inv)
    # Создаем контекст боя для хранения временных данныхs
    context.user_data['fight_context'] = {
        'monster': monster,
        'monster_hp': monster_current_hp,
        'user_hp': user_current_hp,
        'user_mana': user_current_mana,
        'round': current_round,
        'user_energy': user.energy,
        'items': inv,
        'skills': mock_skills,  # Мок навыков
        'buffs': {'attack': 0, 'defense': 0}  # Временные баффы
    }
    
    await send_round_info(update, context, user, monster, current_round)

async def send_round_info(update, context, user, monster, round_num):
    """Отправляет информацию о текущем раунде и кнопки действий"""
    fight_context = context.user_data['fight_context']
    
    # Создаем клавиатуру с доступными действиями
    keyboard = []
    
    # Кнопка обычной атаки
    keyboard.append([InlineKeyboardButton("⚔️ Атаковать", callback_data="fight_attack")])
    
    # Кнопки для предметов (первые 3 мок-предмета)
    for item in fight_context['items'][:3]:
        keyboard.append([InlineKeyboardButton(f"🎒 {item['name']} - {item['count']}шт", 
                                          callback_data=f"fight_useitem_{item['id']}")])
    
    # Кнопки для навыков (первые 3 мок-навыка)
    for skill in fight_context['skills'][:3]:
        keyboard.append([InlineKeyboardButton(f"🔮 {skill['name']} (🔵{skill['mana_cost']})", 
                                          callback_data=f"fight_useskill_{skill['id']}")])
    
    # Кнопка побега (с шансом неудачи)
    keyboard.append([InlineKeyboardButton("🏃 Бежать", callback_data="fight_flee")])
    
    # Отображаем текущие баффы
    buffs_text = ""
    if fight_context['buffs']['attack'] > 0:
        buffs_text += f"\n⚔️ Бафф атаки: +{fight_context['buffs']['attack']}"
    if fight_context['buffs']['defense'] > 0:
        buffs_text += f"\n🛡️ Бафф защиты: +{fight_context['buffs']['defense']}"
    
    message = (
        f"⚔️ Раунд {round_num} ⚔️\n"
        f"Ваше здоровье: {fight_context['user_hp']}/{user.health}\n"
        f"Мана: {fight_context['user_mana']}/{user.mana}\n"
        f"Здоровье {monster.name}: {fight_context['monster_hp']}/{monster.health}\n"
        f"{buffs_text}\n\n"
        f"Выберите действие:"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def fight_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик действий в бою"""
    query = update.callback_query
    await query.answer()
    
    u_tg_id = str(query.from_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()
    fight_context = context.user_data.get('fight_context')
    
    if not fight_context or not user:
        await query.edit_message_text(text="Бой уже завершен.")
        return
    
    monster = fight_context['monster']
    action = query.data.split('_')[1]
    result_message = ""
    
    # Обработка разных действий
    if action == "attack":
        user_attack = calculate_user_attack(user, fight_context['buffs']['attack'])
        monster_damage = max(1, user_attack - monster.defense)
        fight_context['monster_hp'] -= monster_damage
        result_message = f"Вы атаковали и нанесли {monster_damage} урона!"
        
    elif action == "useitem":
        item_id = int(query.data.split('_')[2])
        item = next((i for i in fight_context['items'] if i['id'] == item_id), None)
        if not item:
            result_message = "Предмет не найден!"
        else:
            effect_message = apply_item_effect(user, item, fight_context)
            
            print("Item",item)
            print("Item_id",item_id)
            user.inventory[str(item['id'])] = user.inventory.get(str(item['id']), 0) - 1
            if user.inventory[str(item['id'])] <= 0:
                del user.inventory[str(item['id'])]
                logging.info(f"Предмет {item['name']} удален из инвентаря пользователя {u_tg_id}")

            flag_modified(user, "inventory")
            result_message = f"Вы использовали {item['name']}!\n" + effect_message
            try:
                session.add(user)
                session.commit()
                effect_message = apply_item_effect(user, item, fight_context)
                result_message = f"Вы использовали {item['name']}!\n" + effect_message
            except Exception as e:
                session.rollback()
                logging.error(f"Ошибка при сохранении инвентаря: {e}")
                result_message = "Ошибка при использовании предмета!"
    
    elif action == "useskill":
        skill_id = int(query.data.split('_')[2])
        skill = next((s for s in fight_context['skills'] if s['id'] == skill_id), None)
        if not skill:
            result_message = "Навык не найден!"
        elif fight_context['user_mana'] < skill['mana_cost']:
            result_message = "Недостаточно маны для использования навыка!"
        else:
            effect_message = apply_skill_effect(user, skill, fight_context)
            fight_context['user_mana'] -= skill['mana_cost']
            result_message = f"Вы использовали {skill['name']}!\n" + effect_message
    
    elif action == "flee":
        if random.random() < 0.6:
            user.energy -= 1
            session.commit()
            await query.edit_message_text(
                text="Вы успешно сбежали от монстра! (Энергия -1)",
            )
            context.user_data.pop('fight_context', None)
            return
        else:
            result_message = "Вам не удалось сбежать!"

    # Проверка на победу игрока
    if fight_context['monster_hp'] <= 0:
        reward_gold = random.randint(10, 20) * fight_context['round']
        reward_xp = random.randint(20, 30) * fight_context['round']
        
        user.gold += reward_gold
        user.xp += reward_xp
        user.energy -= 1
        session.commit()
        
        await query.edit_message_text(
            text=f"{result_message}\n\nВы победили монстра {monster.name}!\n"
                 f"Получено: {reward_gold} золота и {reward_xp} опыта."
        )
        context.user_data.pop('fight_context', None)
        return
    
    # Монстр атакует в ответ (если игрок не убежал)
    if action != "flee":
        monster_attack = calculate_monster_attack(monster)
        user_defense = user.defense + fight_context['buffs']['defense']
        user_damage = max(1, monster_attack - user_defense)
        fight_context['user_hp'] -= user_damage
        result_message += f"\n{monster.name} атакует в ответ и наносит {user_damage} урона!"
    
    # Проверка на поражение игрока (должна быть после атаки монстра)
    if fight_context['user_hp'] <= 0:
        user.energy -= 1
        session.commit()
        
        # Очищаем контекст боя перед отправкой сообщения
        context.user_data.pop('fight_context', None)
        await query.edit_message_text(
            text=f"{result_message}\n\nВы проиграли в бою с {monster.name}! (Энергия -1)",
        )
        return
    
    # Уменьшаем длительность баффов
    if fight_context['buffs']['attack'] > 0:
        fight_context['buffs']['attack'] = max(0, fight_context['buffs']['attack'] - 1)
    if fight_context['buffs']['defense'] > 0:
        fight_context['buffs']['defense'] = max(0, fight_context['buffs']['defense'] - 1)
    
    # Переход к следующему раунду
    fight_context['round'] += 1
    await query.edit_message_text(text=result_message)
    await send_round_info(update, context, user, monster, fight_context['round'])

def calculate_user_attack(user, attack_buff=0):
    """Рассчитывает урон игрока с учетом баффов"""
    base_attack = user.attack + attack_buff
    # Добавляем случайный элемент (от -10% до +10% от базового урона)
    final_attack = base_attack + random.randint(-base_attack // 10, base_attack // 10)
    return max(1, final_attack)

def calculate_monster_attack(monster):
    """Рассчитывает урон монстра"""
    base_attack = monster.attack
    # Добавляем случайный элемент (от -15% до +15% от базового урона)
    final_attack = base_attack + random.randint(-base_attack * 15 // 100, base_attack * 15 // 100)
    return max(1, final_attack)

def apply_item_effect(user, item, fight_context):
    """Применяет эффект мок-предмета и возвращает сообщение о результате"""
    effect_message = ""
    
    if item['type'] == "heal":
        heal_amount = item['power']
        max_hp = user.health
        fight_context['user_hp'] = min(max_hp, fight_context['user_hp'] + heal_amount)
        effect_message = f"Восстановлено {heal_amount} здоровья."
    
    elif item['type'] == "buff_attack":
        fight_context['buffs']['attack'] = item['power']
        effect_message = f"Ваша атака увеличена на {item['power']} на 3 раунда."
    
    elif item['type'] == "escape":
        # Автоматический побег
        user.energy -= 1
        session.commit()
        effect_message = "Вы использовали дымовую шашку и сбежали!"
        fight_context['user_hp'] = 0  # Завершаем бой
    
    return effect_message

def apply_skill_effect(user, skill, fight_context):
    """Применяет эффект мок-навыка и возвращает сообщение о результате"""
    effect_message = ""
    
    if skill['type'] == "damage":
        damage = skill['power'] + user.magic_attack // 2
        fight_context['monster_hp'] -= damage
        effect_message = f"Нанесено {damage} магического урона."
    
    elif skill['type'] == "heal":
        heal_amount = skill['power'] + user.magic_attack // 2
        max_hp = user.health
        fight_context['user_hp'] = min(max_hp, fight_context['user_hp'] + heal_amount)
        effect_message = f"Восстановлено {heal_amount} здоровья."
    
    elif skill['type'] == "buff_defense":
        fight_context['buffs']['defense'] = skill['power']
        effect_message = f"Ваша защита увеличена на {skill['power']} на 3 раунда."
    
    return effect_message

ITEMS = {
    "sword": {"name": "🗡 Меч рыцаря", "attack": 5, "cost": 20},
    "shield": {"name": "🛡 Щит стража", "defense": 3, "cost": 15},
    "potion": {"name": "🧪 Зелье здоровья", "heal": 10, "cost": 5}
}

# 🏪 Команда /shop — Магазин
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    items = session.query(Item).filter(Item.price > 0).order_by(Item.price).all()
    
    if not items:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏪 Магазин пуст! Попробуйте позже.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    keyboard = [
        [InlineKeyboardButton(
            f"{item.name} - {item.price}💰", 
            callback_data=f"buy_{item.item_id}"
        )] 
        for item in items
    ]
    #keyboard = [
     #   [InlineKeyboardButton(f"{item['name']} - {item['cost']}💰", callback_data=f"buy_{key}")]
     #   for key, item in ITEMS.items()
    #]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if user:
        shop_text = (
            f"🏪 *Магазин*\n"
            f"💰 Ваше золото: *{user.gold}*\n\n"
            "Выберите предмет для покупки:"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=shop_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сначала создайте персонажа с помощью /start.",
            reply_markup=main_menu_keyboard()
        )

# 🛒 Покупка предмета
async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Разбираем callback_data
    data = query.data.split("_")  # Получим ['buy', 'sword'] или ['buy', 'shield']
    try:
        item_id = int(data[1])
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Ошибка: неверный ID предмета!")
        logging.error(f"Неверный формат callback_data: {query.data}")
        return

    item = session.query(Item).filter_by(item_id=item_id).first()
    if not item:
        await query.message.reply_text("❌ Ошибка: предмет не найден!")
        logging.error(f"Предмет с ID {item_id} не найден в базе данных.")
        return

    # Получаем пользователя
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if not user:
        await query.message.reply_text("❌ Сначала создайте персонажа с помощью /start.")
        logging.error(f"Пользователь с tg_id={u_tg_id} не найден в базе данных.")
        return

    # Проверяем, хватает ли золота
    if user.gold < item.price:
        await query.message.reply_text(f"💰 Недостаточно золота! Нужно {item.price}💰, у вас {user.gold}💰")
        logging.warning(f"У пользователя {u_tg_id} недостаточно золота для покупки {item.name}.")
        return
   
    # Обновляем инвентарь
    if user.inventory is None or not isinstance(user.inventory, dict):
        user.inventory = {}
        logging.info(f"Инвентарь пользователя {u_tg_id} инициализирован как пустой словарь.")

    # Добавляем предмет в инвентарь (используем item_id как ключ)
    user.inventory[str(item.item_id)] = user.inventory.get(str(item.item_id), 0) + 1
    flag_modified(user, "inventory")

    # Применяем бонусы предмета (если есть)
    #if item.attack_bonus > 0:
    #   user.attack += item.attack_bonus
    #if item.defense_bonus > 0:
    #    user.defense += item.defense_bonus
        
    # Вычитаем золото
    user.gold -= item.price
    session.add(user)

    try:
        session.commit()
        logging.info(f"Покупка: пользователь {u_tg_id} купил {item.name} за {item.price}💰")
        
        # Формируем сообщение о покупке
        #bonus_text = ""
        #if item.attack_bonus > 0:
        #    bonus_text += f"\n⚔️ +{item.attack_bonus} к атаке"
        #if item.defense_bonus > 0:
        #    bonus_text += f"\n🛡 +{item.defense_bonus} к защите"
        
        await query.message.reply_text(
            f"✅ Вы купили {item.name} за {item.price}💰!\n"
            f"💰 Остаток: {user.gold}💰"
        )

        # Обновляем магазин
        await shop(update, context)
        
    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при покупке: {e}")
        await query.message.reply_text("❌ Произошла ошибка при сохранении данных. Попробуйте еще раз.")

# Команда /quest — квесты (заглушка)
async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ЕЩЕ НЕ РАБОТАЕТ",
        reply_markup=main_menu_keyboard()
    )



# Основная функция
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile))
    application.add_handler(MessageHandler(filters.Regex("⚔️ Сразиться с монстром"), fight))
    application.add_handler(MessageHandler(filters.Regex("🛒 Магазин"), shop))
    #application.add_handler(MessageHandler(filters.Regex("📜 Квесты"), quest))
    application.add_handler(CallbackQueryHandler(fight_action, pattern="^fight_"))
    application.add_handler(CallbackQueryHandler(buy_item, pattern="^buy"))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запуск бота
    application.run_polling()