# api/services/shop_service.py

from back.db.db import User, Item
from back.db.dbSession import session
from sqlalchemy.orm.attributes import flag_modified

def get_shop_items(tg_id: str):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    if not user:
        return {"error": "Сначала создайте персонажа."}

    items = session.query(Item).filter(Item.price > 0).order_by(Item.price).all()
    
    item_list = []
    for item in items:
        item_list.append({
            "id": item.item_id, 
            "name": item.name, 
            "price": item.price})

    return {
        "message": "🏪 Магазин открыт!",
        "user_gold": user.gold,
        "items": item_list
    }

def buy_item(tg_id: str, item_id: int):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    item = session.query(Item).filter_by(item_id=item_id).first()

    if not user:
        return {"error": "Сначала создайте персонажа."}
    if not item:
        return {"error": "Предмет не найден."}
    if user.gold < item.price:
        return {"message": f"Недостаточно золота. Нужно {item.price}💰, у вас {user.gold}💰"}

    if user.inventory is None or not isinstance(user.inventory, dict):
        user.inventory = {}

    user.inventory[str(item.item_id)] = user.inventory.get(str(item.item_id), 0) + 1
    flag_modified(user, "inventory")
    user.gold -= item.price

    try:
        session.add(user)
        session.commit()
        return {
            "message": f"✅ Вы купили {item.name} за {item.price}💰!",
            "user_gold": user.gold
        }
    except Exception:
        session.rollback()
        return {"error": "Ошибка при сохранении покупки."}
