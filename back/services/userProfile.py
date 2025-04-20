# api/services/profile_service.py

from db.db import Quest, User, Item
from db.dbSession import session

def get_profile(tg_id: str):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    if not user:
        return {"error": "Сначала создайте персонажа."}

    inventory_items = user.inventory if isinstance(user.inventory, dict) else {}
    inventory = []

    if inventory_items:
        item_ids = [int(item_id) for item_id in inventory_items.keys()]
        items = session.query(Item).filter(Item.item_id.in_(item_ids)).all()

        item_dict = {str(item.item_id): item for item in items}
        for item_id, count in inventory_items.items():
            item = item_dict.get(item_id)
            if item:
                line = f"{item.name}: {count} шт."
                if item.attack_bonus > 0:
                    line += f" (+{item.attack_bonus}⚔)"
                if item.defense_bonus > 0:
                    line += f" (+{item.defense_bonus}🛡)"
                inventory.append(line)


    energy_bar = f"⚡ Энергия: {user.energy}/10"
    profile_text = (
        f"👤 Профиль {user.username}\n"
        f"🏅 Класс: {user.class_}\n"
        f"⚜️ Уровень: {user.level} (XP: {user.xp}/{user.level * 100 + 100})\n"
        f"❤️ HP: {user.health}   🔮 Mana: {user.mana}\n"
        f"⚔️ Атака: {user.attack}   🛡 Защита: {user.defense}\n"
        f"💰 Золото: {user.gold}\n"
        f"{energy_bar}\n\n"
        f"🎒 Инвентарь:\n" + ("\n".join(inventory) if inventory else "📭 Пусто")
    )
    if user.active_quest_id:
        quest = session.query(Quest).get(user.active_quest_id)
        progress = user.quest_progress
        profile_text += f"\n📌 Активный квест: {quest.name} ({progress}/{quest.required})"

    return {
        "message": profile_text
    }
