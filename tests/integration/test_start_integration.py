def test_create_user_and_choose_class(db_session):
    from back.services import start

    res = start.create_user("tg001", "TestUser")
    assert res["message"] == "Выберите класс:"
    assert "classes" in res

    res2 = start.choose_class("tg001", "mage", "TestUser")
    assert res2["message"].startswith("Вы выбрали класс Mage")

    user = start.session.query(start.User).filter_by(tg_id="tg001").first()
    assert user is not None
    assert user.class_ == "Mage"
