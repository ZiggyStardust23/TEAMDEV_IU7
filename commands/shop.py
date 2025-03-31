import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes
)
from sqlalchemy.orm.attributes import flag_modified
from db.db import Item, User
from db.dbSession import session
from gui.keyboards import main_menu_keyboard

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

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
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

    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if not user:
        await query.message.reply_text("❌ Сначала создайте персонажа с помощью /start.")
        logging.error(f"Пользователь с tg_id={u_tg_id} не найден в базе данных.")
        return

    if user.gold < item.price:
        await query.message.reply_text(f"💰 Недостаточно золота! Нужно {item.price}💰, у вас {user.gold}💰")
        logging.warning(f"У пользователя {u_tg_id} недостаточно золота для покупки {item.name}.")
        return
   
    if user.inventory is None or not isinstance(user.inventory, dict):
        user.inventory = {}
        logging.info(f"Инвентарь пользователя {u_tg_id} инициализирован как пустой словарь.")

    user.inventory[str(item.item_id)] = user.inventory.get(str(item.item_id), 0) + 1
    flag_modified(user, "inventory")
        
    user.gold -= item.price
    session.add(user)

    try:
        session.commit()
        logging.info(f"Покупка: пользователь {u_tg_id} купил {item.name} за {item.price}💰")
        
        await query.message.reply_text(
            f"✅ Вы купили {item.name} за {item.price}💰!\n"
            f"💰 Остаток: {user.gold}💰"
        )

        await shop(update, context)
        
    except Exception as e:
        session.rollback()
        logging.error(f"Ошибка при покупке: {e}")
        await query.message.reply_text("❌ Произошла ошибка при сохранении данных. Попробуйте еще раз.")