from telegram import Update
from telegram.ext import (
    ContextTypes
)
from db.db import Item, User
from db.dbSession import session
from gui.keyboards import main_menu_keyboard

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

    inventory_items = user.inventory if isinstance(user.inventory, dict) else {}
    inventory_text = "📭 Пусто"
    
    if inventory_items:
        item_ids = [int(item_id) for item_id in inventory_items.keys()]
        items = session.query(Item).filter(Item.item_id.in_(item_ids)).all() if item_ids else []
        
        items_dict = {str(item.item_id): item for item in items}
        
        inventory_lines = []
        for item_id, count in inventory_items.items():
            item = items_dict.get(item_id)
            if item:
                line = f"🔹 {item.name}: {count} шт."
            #    if item.attack_bonus > 0:
            #        line += f" (+{item.attack_bonus}⚔)"
            #    if item.defense_bonus > 0:
            #        line += f" (+{item.defense_bonus}🛡)"
                inventory_lines.append(line)
        
        inventory_text = "\n".join(inventory_lines) if inventory_lines else "📭 Пусто"

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

    energy_bar = "⚡LITENERGY⚡" #⚡[" + "█" * user.energy + "░" * (10 - user.energy) + "]"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{profile_text}\n\n{energy_bar}",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )