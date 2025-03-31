from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes
)
from db.db import User
from db.dbSession import session
from gui.keyboards import main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_tg_id = str(update.effective_user.id)

    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы уже создали персонажа!",
            reply_markup=main_menu_keyboard()
        )
    else:
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
        reply_markup=None
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_markup=main_menu_keyboard()
    )