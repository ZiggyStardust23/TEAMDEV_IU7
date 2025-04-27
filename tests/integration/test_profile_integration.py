def test_get_profile(db_session):
    from back.services import start, userProfile

    # Создаём персонажа
    start.choose_class("tg005", "warrior")

    res = userProfile.get_profile("tg005")
    assert "👤 Профиль" in res["message"]
    assert "🏅 Класс: Warrior" in res["message"]
