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
from db import Base, User, Monster  # Импортируем модели из файла models.py
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

    if user:
        # Форматирование инвентаря
        inventory_items = user.inventory if user.inventory else {}
        inventory_text = "\n".join(
            [f"🔹 {ITEMS[key]['name']}: {value} шт." for key, value in inventory_items.items()]
        ) if inventory_items else "📭 Пусто"

        # Формирование текста профиля
        profile_text = (
            f"👤 *Профиль*\n"
            f"📛 Имя: *{user.username}*\n"
            f"🛡 Класс: *{user.class_}*\n"
            f"📈 Уровень: *{user.level}*\n"
            f"⭐ Опыт: *{user.xp}*\n"
            f"❤️ Здоровье: *{user.health}*\n"
            f"🔮 Мана: *{user.mana}*\n"
            f"⚔️ Атака: *{user.attack}*\n"
            f"🛡 Защита: *{user.defense}*\n"
            f"💰 Золото: *{user.gold}*\n"
            f"⚡ Энергия: *{user.energy}*\n\n"
            f"🎒 *Инвентарь:*\n{inventory_text}"
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=profile_text,
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Сначала создайте персонажа с помощью /start.",
            reply_markup=main_menu_keyboard()
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
    keyboard = [
        [InlineKeyboardButton(f"{item['name']} - {item['cost']}💰", callback_data=f"buy_{key}")]
        for key, item in ITEMS.items()
    ]
    
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
    item_key = data[1]  # 'sword', 'shield' и т.д.

    if item_key not in ITEMS:
        await query.message.reply_text("❌ Ошибка: предмет не найден!")
        logging.error(f"Предмет {item_key} не найден в ITEMS.")
        return

    item = ITEMS[item_key]
    item_name = item["name"]
    item_price = item["cost"]

    # Получаем пользователя
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if not user:
        await query.message.reply_text("❌ Сначала создайте персонажа с помощью /start.")
        logging.error(f"Пользователь с tg_id={u_tg_id} не найден в базе данных.")
        return

    # Проверяем, хватает ли золота
    if user.gold < item_price:
        await query.message.reply_text("💰 Недостаточно золота!")
        logging.warning(f"У пользователя {u_tg_id} недостаточно золота для покупки {item_name}.")
        return

    # Обновляем инвентарь
    if user.inventory is None or not isinstance(user.inventory, dict):
        user.inventory = {}
        logging.info(f"Инвентарь пользователя {u_tg_id} инициализирован как пустой словарь.")

    # Добавляем предмет в инвентарь
    user.inventory[item_key] = user.inventory.get(item_key, 0) + 1  # Увеличиваем количество
    flag_modified(user, "inventory")  # Уведомляем SQLAlchemy об изменении
    logging.info(f"Предмет {item_name} добавлен в инвентарь пользователя {u_tg_id}. Текущий инвентарь: {user.inventory}")

    # Вычитаем золото
    user.gold -= item_price
    logging.info(f"У пользователя {u_tg_id} списано {item_price} золота. Остаток: {user.gold}")

    # Явно добавляем пользователя в сессию, чтобы SQLAlchemy отследил изменения
    session.add(user)
    try:
        session.commit()
        logging.info(f"Изменения для пользователя {u_tg_id} успешно сохранены в базе данных.")
    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при сохранении изменений в базе данных: {e}")
        await query.message.reply_text("❌ Произошла ошибка при сохранении данных. Попробуйте еще раз.")
        return

    # Отправляем подтверждение покупки
    await query.message.reply_text(f"✅ Вы купили {item_name} за {item_price}💰!")

    # Обновляем магазин
    await shop(update, context)

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
