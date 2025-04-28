# api/services/start_service.py

from back.db.dbSession import session
from back.db.db import Skill, User

CLASS_PRESETS = {
    "mage": {
        "class_": "Mage",
        "health": 80,
        "mana": 100,
        "attack": 8,
        "defense": 3,
        "skills": ["Огненный шар", "Ледяная тюрьма", "Энергетический всплеск"]
    },
    "warrior": {
        "class_": "Warrior",
        "health": 100,
        "mana": 50,
        "attack": 10,
        "defense": 5,
        "skills": ["Разрубающий удар", "Берсерк", "Землетрясение"]
    },
    "archer": {
        "class_": "Archer",
        "health": 90,
        "mana": 60,
        "attack": 12,
        "defense": 4,
        "skills": ["Снайперский выстрел", "Дождь стрел", "Ядовитая стрела"]
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

def choose_class(tg_id: str, chosen: str, username: str):
    if chosen not in CLASS_PRESETS:
        return {"error": "Неверный класс"}

    existing = session.query(User).filter_by(tg_id=tg_id).first()
    if existing:
        return {"message": "Персонаж уже существует."}

    cls = CLASS_PRESETS[chosen]

    # Получаем реальные skill_id по именам
    skill_names = cls["skills"]
    skills = session.query(Skill).filter(Skill.name.in_(skill_names)).all()
    skill_ids = [str(skill.skill_id) for skill in skills]

    user = User(
        tg_id=tg_id,
        username=username,
        class_=cls["class_"],
        level=1,
        xp=0,
        health=cls["health"],
        mana=cls["mana"],
        attack=cls["attack"],
        defense=cls["defense"],
        gold=0,
        energy=100,
        abilities={"skills": skill_ids},
        inventory={}
    )

    session.add(user)
    session.commit()
    return {"message": f"Вы выбрали класс {cls['class_']}. Персонаж создан!"}
