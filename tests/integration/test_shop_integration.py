def test_buy_item(db_session):
    from back.services import start, shop
    from back.db.db import Item

    # Создаём персонажа
    start.choose_class("tg003", "archer")
    user = shop.session.query(shop.User).filter_by(tg_id="tg003").first()
    user.gold = 100

    # Добавляем предмет
    item = Item(name="Potion", type="heal", power=30, price=10)
    db_session.add(item)
    db_session.commit()

    res = shop.buy_item("tg003", item_id=item.item_id)
    assert res["message"].startswith("✅ Вы купили")
    updated_user = shop.session.query(shop.User).filter_by(tg_id="tg003").first()
    assert updated_user.inventory.get(str(item.item_id)) == 1
