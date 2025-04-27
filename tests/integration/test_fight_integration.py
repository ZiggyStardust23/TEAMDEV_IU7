def test_fight_start_and_attack(db_session):
    from back.services import start, fight
    from back.db.db import Monster

    # Создаём персонажа
    start.choose_class("tg002", "warrior", "TestUser")

    # Добавляем монстра
    monster = Monster(name="TestMonster", attack=5, health=50)
    db_session.add(monster)
    db_session.commit()

    res = fight.fight_start("tg002")
    assert "fight" in res
    assert res["fight"]["monster_name"] == "TestMonster"

    res2 = fight.fight_action("tg002", "attack")
    assert "message" in res2
    assert "атакует" in res2["message"] or "Вы нанесли" in res2["message"]
