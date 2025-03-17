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
    tg_id = update.effective_user.id
    username = update.effective_user.username

    # Проверяем, есть ли пользователь в базе
    user = session.query(User).filter_by(tg_id=tg_id).first()

    if user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы уже создали персонажа!",
            reply_markup=main_menu_keyboard()
        )
    else:
        # Создаем нового персонажа
        new_user = User(
            tg_id=tg_id,
            username=username,
            class_="Warrior",
            level=1,
            xp=0,
            health=100,
            mana=50,
            attack=10,
            defense=5,
            gold=0,
            energy=10,
            abilities={"skill1": "Fireball"},
            inventory={"item1": "Sword"}
        )
        session.add(new_user)
        session.commit()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Персонаж создан! Вы — Воин.",
            reply_markup=main_menu_keyboard()
        )

# Команда /profile — просмотр профиля
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = session.query(User).filter_by(user_id=user_id).first()

    if user:
        profile_text = (
            f"👤 Профиль:\n"
            f"Имя: {user.username}\n"
            f"Класс: {user.class_}\n"
            f"Уровень: {user.level}\n"
            f"Опыт: {user.xp}\n"
            f"Здоровье: {user.health}\n"
            f"Мана: {user.mana}\n"
            f"Атака: {user.attack}\n"
            f"Защита: {user.defense}\n"
            f"Золото: {user.gold}\n"
            f"Энергия: {user.energy}\n"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=profile_text,
            reply_markup=main_menu_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сначала создайте персонажа с помощью /start.",
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
# Обработка inline-кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "continue":
        await query.edit_message_text(
            text="Вы готовы к новым приключениям!",
            reply_markup=main_menu_keyboard()
        )


# Основная функция
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex("👤 Профиль"), profile))
    #application.add_handler(MessageHandler(filters.Regex("⚔️ Сразиться с монстром"), fight))
    #application.add_handler(MessageHandler(filters.Regex("🛒 Магазин"), shop))
    #application.add_handler(MessageHandler(filters.Regex("📜 Квесты"), quest))

    # Обработчик inline-кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    application.run_polling()