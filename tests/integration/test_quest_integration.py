def test_accept_and_cancel_quest(db_session):
    from back.services import start, quest
    from back.db.db import Quest

    # Создаём персонажа
    start.choose_class("tg004", "mage", "TestUser")

    # Добавляем квест
    quest_it = Quest(name="Test Quest", quest_type="kill", target="1", required=1, reward_gold=10, reward_xp=5)
    db_session.add(quest_it)
    db_session.commit()

    res = quest.handle_quest("tg004", "accept", quest_id=quest_it.quest_id)
    assert res["message"] == "🎉 Квест принят!"

    res2 = quest.handle_quest("tg004", "cancel")
    assert res2["message"] == "Квест отменён."
