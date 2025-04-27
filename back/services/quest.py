# api/services/quest_service.py

from sqlalchemy import not_
from back.db.dbSession import session
from back.db.db import User, Quest
from sqlalchemy.orm.attributes import flag_modified

def get_quest_progress(user: User, quest: Quest):
    if quest.quest_type == "kill":
        return user.quest_progress
    elif quest.quest_type == "collect":
        return user.inventory.get(str(quest.target), 0)
    return 0

def check_quest_completion(user: User):
    if not user.active_quest_id:
        return False

    quest = session.query(Quest).get(user.active_quest_id)
    progress = get_quest_progress(user, quest)

    if progress >= quest.required:
        user.gold += quest.reward_gold
        user.xp += quest.reward_xp

        if quest.reward_item_id:
            user.inventory[str(quest.reward_item_id)] = user.inventory.get(str(quest.reward_item_id), 0) + 1
            flag_modified(user, "inventory")

        if not user.completed_quests:
            user.completed_quests = []
        user.completed_quests.append(quest.quest_id)
        flag_modified(user, "completed_quests")

        user.active_quest_id = None
        user.quest_progress = 0
        session.commit()
        return True
    return False

def handle_quest(tg_id: str, action: str, quest_id: int = None):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    if not user:
        return {"error": "Сначала создайте персонажа."}

    if action == "current":
        quest = session.query(Quest).get(user.active_quest_id)
        progress = get_quest_progress(user, quest)
        return {
            "message": f"📌 {quest.name}\n{quest.description}\nПрогресс: {progress}/{quest.required}"
        }

    elif action == "cancel":
        user.active_quest_id = None
        user.quest_progress = 0
        session.commit()
        return {"message": "Квест отменён."}

    elif action == "accept":
        if not quest_id:
            return {"error": "Не указан quest_id."}
        user.active_quest_id = quest_id
        user.quest_progress = 0
        session.commit()
        return {"message": "🎉 Квест принят!"}

    else:
        # default — показать доступные
        available = session.query(Quest).filter(
            Quest.min_level <= user.level,
            not_(Quest.quest_id.in_(user.completed_quests)) if user.completed_quests else True
        ).limit(3).all()

        quests = [{
            "id": q.quest_id,
            "name": q.name,
            "level": q.min_level
        } for q in available]

        return {
            "message": "📜 Доступные квесты:",
            "quests": quests
        }
