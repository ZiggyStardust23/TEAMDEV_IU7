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
from db import Base, User, Monster, Item, Quest  # Импортируем модели из файла models.py
from sqlalchemy.orm.attributes import flag_modified

# Настройки подключения к базе данных
DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@localhost:5432/teamdev'

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URI)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

# Токен вашего бота
TOKEN = '8110578388:AAEDoVcDY4p7MKAFywEvxj4VLE3Ugc9AL5o'

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
    else:
        # Если data неизвестная, выводим сообщение и прекращаем выполнение
        await query.edit_message_text(text="❌ Ошибка: выбранный класс не найден.", reply_markup=None)
        return  

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
        text="🎮 Главное меню",
        reply_markup=main_menu_keyboard()
    )

# 📜 Команда /profile — просмотр профиля с инвентарем
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
    energy_bar = "⚡[" + "█" * user.energy + "░" * (10 - user.energy) + "]"
    
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
'''
# Команда /fight — битва с монстром
async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = session.query(User).filter_by(user_id=user_id).first()

    if not user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сначала создайте персонажа с помощью /start.",
            reply_markup=main_menu_keyboard()
        )
        return

    # Проверяем, есть ли у пользователя энергия
    if user.energy <= 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="У вас закончилась энергия. Подождите, пока она восстановится.",
            reply_markup=main_menu_keyboard()
        )
        return

    # Выбираем случайного монстра
    monster = session.query(Monster).order_by(Monster.monster_id).first()

    if monster:
        # Логика боя (упрощенная)
        user_attack = random.randint(5, 15)  # Случайная атака пользователя
        monster_damage = max(0, user_attack - monster.defense)
        monster.health -= monster_damage

        if monster.health <= 0:
            # Пользователь победил
            reward_gold = random.randint(10, 20)
            reward_xp = random.randint(20, 30)

            user.gold += reward_gold
            user.xp += reward_xp
            user.energy -= 1
            session.commit()

            # Кнопка "Продолжить"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Продолжить", callback_data="continue")]
            ])

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Вы победили монстра {monster.name}!\n"
                     f"Получено: {reward_gold} золота и {reward_xp} опыта.",
                reply_markup=keyboard
            )
        else:
            # Монстр победил
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Монстр {monster.name} оказался слишком сильным! Вы проиграли.",
                reply_markup=main_menu_keyboard()
            )

# Команда /shop — магазин (заглушка)
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ЕЩЕ НЕ РАБОТАЕТ",
        reply_markup=main_menu_keyboard()
    )

# Команда /quest — квесты (заглушка)
async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ЕЩЕ НЕ РАБОТАЕТ",
        reply_markup=main_menu_keyboard()
    )
'''
# Команда /shop — магазин (заглушка)
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
    if item.attack_bonus > 0:
        user.attack += item.attack_bonus
    if item.defense_bonus > 0:
        user.defense += item.defense_bonus
        
    # Вычитаем золото
    user.gold -= item.price
    session.add(user)

    try:
        session.commit()
        logging.info(f"Покупка: пользователь {u_tg_id} купил {item.name} за {item.price}💰")
        
        # Формируем сообщение о покупке
        bonus_text = ""
        if item.attack_bonus > 0:
            bonus_text += f"\n⚔️ +{item.attack_bonus} к атаке"
        if item.defense_bonus > 0:
            bonus_text += f"\n🛡 +{item.defense_bonus} к защите"
        
        await query.message.reply_text(
            f"✅ Вы купили {item.name} за {item.price}💰!{bonus_text}\n"
            f"💰 Остаток: {user.gold}💰"
        )

        # Обновляем магазин
        await shop(update, context)
        
    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при покупке: {e}")
        await query.message.reply_text("❌ Произошла ошибка при сохранении данных. Попробуйте еще раз.")

# Основная функция
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile))
    application.add_handler(MessageHandler(filters.Regex("🛒 Магазин"), shop))

    application.add_handler(CallbackQueryHandler(button_callback, pattern="^class_"))  # Выбор класса
    application.add_handler(CallbackQueryHandler(buy_item, pattern="^buy_"))  # Покупка предмета

    # Запуск бота
    application.run_polling()
