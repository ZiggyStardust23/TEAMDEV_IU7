# api/services/start_service.py

from db.dbSession import session
from db.db import User

CLASS_PRESETS = {
    "mage": {
        "class_": "Mage",
        "health": 80,
        "mana": 100,
        "attack": 8,
        "defense": 3,
        "skills": ["1", "2", "3"]
    },
    "warrior": {
        "class_": "Warrior",
        "health": 100,
        "mana": 50,
        "attack": 10,
        "defense": 5,
        "skills": ["4", "5", "6"]
    },
    "archer": {
        "class_": "Archer",
        "health": 90,
        "mana": 60,
        "attack": 12,
        "defense": 4,
        "skills": ["7", "8", "9"]
    }
}

def create_user(tg_id: str, username: str):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    if user:
        return {"message": "Вы уже создали персонажа."}

    return {
        "message": "Выберите класс:",
        "classes": ["mage", "warrior", "archer"]
    }

def choose_class(tg_id: str, chosen: str):
    if chosen not in CLASS_PRESETS:
        return {"error": "Неверный класс"}

    existing = session.query(User).filter_by(tg_id=tg_id).first()
    if existing:
        return {"message": "Персонаж уже существует."}

    cls = CLASS_PRESETS[chosen]
    user = User(
        tg_id=tg_id,
        username="user",
        class_=cls["class_"],
        level=1,
        xp=0,
        health=cls["health"],
        mana=cls["mana"],
        attack=cls["attack"],
        defense=cls["defense"],
        gold=0,
        energy=10,
        abilities={"skills": cls["skills"]},
        inventory={}
    )

    session.add(user)
    session.commit()
    return {"message": f"Вы выбрали класс {cls['class_']}. Персонаж создан!"}
