# api/services/fight_service.py

from random import choice, randint
from db.dbSession import session
from db.db import User, Monster, Skill, Item, Quest
from sqlalchemy.orm.attributes import flag_modified

def get_random_monster():
    monsters = session.query(Monster).all()
    return choice(monsters)

def calculate_user_attack(user, attack_buff=0):
    base_attack = user.attack + attack_buff
    return max(1, base_attack + randint(-base_attack // 10, base_attack // 10))

def calculate_monster_attack(monster):
    base_attack = monster.attack
    return max(1, base_attack + randint(-base_attack * 15 // 100, base_attack * 15 // 100))

def fight_start(tg_id: str):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    if not user:
        return {"error": "Сначала создайте персонажа."}
    if user.energy <= 0:
        return {"message": "У вас закончилась энергия."}
    
        # Список предметов
    inventory_items = user.inventory or {}
    items = []
    if inventory_items:
        item_ids = [int(i) for i in inventory_items.keys()]
        db_items = session.query(Item).filter(Item.item_id.in_(item_ids)).all()
        item_map = {str(i.item_id): i for i in db_items}
        for item_id, count in inventory_items.items():
            item = item_map.get(item_id)
            if item:
                items.append({
                    "id": item.item_id,
                    "name": item.name,
                    "count": count,
                    "type": item.type
                })

    # Список навыков
    skill_ids = user.abilities.get("skills", [])
    skills = []
    if skill_ids:
        db_skills = session.query(Skill).filter(Skill.skill_id.in_([int(i) for i in skill_ids])).all()
        for sk in db_skills:
            skills.append({
                "id": sk.skill_id,
                "name": sk.name,
                "mana_cost": sk.mana_cost,
                "type": sk.type
            })

    monster = get_random_monster()
    fight_context = {
        "monster_id": monster.monster_id,
        "monster_name": monster.name,
        "monster_hp": monster.health,
        "user_hp": user.health,
        "user_mana": user.mana,
        "max_hp": user.health,
        "round": 1,
        "buffs": {"attack": 0, "defense": 0}
    }
    
    fight_context["items"] = items
    fight_context["skills"] = skills

    user.abilities = user.abilities or {}
    user.abilities["fight_context"] = fight_context
    flag_modified(user, "abilities")
    session.commit()

    return {
        "message": f"Вы вступили в бой с {monster.name}!",
        "fight": fight_context,
        "round": fight_context["round"],
        "actions": ["attack", "flee", "useitem", "useskill"],
        "items": fight_context["items"],
        "skills": fight_context.get("skills", [])
    }

def fight_action(tg_id: str, action: str, skill_id: int = None, item_id: int = None):
    user = session.query(User).filter_by(tg_id=tg_id).first()
    if not user:
        return {"error": "Пользователь не найден."}

    fc = dict(user.abilities.get("fight_context", {}))  # копия
    if not fc:
        return {"message": "Бой не начат."}

    monster = session.query(Monster).filter_by(monster_id=fc["monster_id"]).first()
    if not monster:
        return {"error": "Монстр не найден."}

    msg = ""

    if action == "attack":
        dmg = calculate_user_attack(user, fc["buffs"].get("attack", 0))
        fc["monster_hp"] -= dmg
        msg += f"Вы нанесли {dmg} урона монстру {fc['monster_name']}."

    elif action == "flee":
        if randint(0, 100) < 60:
            user.energy -= 1
            user.abilities.pop("fight_context", None)
            flag_modified(user, "abilities")
            session.commit()
            return {"message": "Вы успешно сбежали! Энергия -1"}
        else:
            msg += "Не удалось сбежать."

    elif action == "useskill" and skill_id:
        skills = user.abilities.get("skills", [])
        if str(skill_id) not in skills:
            return {"message": "У вас нет такого навыка."}
        skill = session.query(Skill).filter_by(skill_id=skill_id).first()
        if fc["user_mana"] < skill.mana_cost:
            return {"message": "Недостаточно маны."}
        fc["user_mana"] -= skill.mana_cost
        if skill.type == "damage":
            dmg = int(skill.power * (100 + user.level) / 100)
            fc["monster_hp"] -= dmg
            msg += f"Навык {skill.name}: вы нанесли {dmg} урона."
        elif skill.type == "heal":
            heal = int(skill.power + (100 + user.level) / 100)
            fc["user_hp"] = min(user.health, fc["user_hp"] + heal)
            msg += f"Навык {skill.name}: вы восстановили {heal} HP."
        elif skill.type == "buff_attack":
            fc["buffs"]["attack"] = skill.power
            msg += f"Атака +{skill.power}."
        elif skill.type == "buff_defense":
            fc["buffs"]["defense"] = skill.power
            msg += f"Защита +{skill.power}."

    elif action == "useitem" and item_id:
        inv = dict(user.inventory or {})
        item_key = str(item_id)

        if item_key not in inv or inv[item_key] <= 0:
            return {"message": "Нет такого предмета."}

        item = session.query(Item).filter_by(item_id=item_id).first()

        if item.type == "heal":
            fc["user_hp"] = min(user.health, fc["user_hp"] + item.power)
            msg += f"Вы использовали {item.name}, восстановлено {item.power} HP."
        elif item.type == "buff_attack":
            fc["buffs"]["attack"] = item.power
            msg += f"Атака +{item.power}."
        elif item.type == "escape":
            user.energy -= 1
            user.abilities.pop("fight_context", None)
            flag_modified(user, "abilities")
            session.commit()
            return {"message": "Вы использовали дымовую шашку и сбежали!"}
        
        # Списываем из инвентаря
        inv[item_key] -= 1
        if inv[item_key] <= 0:
            del inv[item_key]
        user.inventory = inv.copy()
        flag_modified(user, "inventory")

        # Списываем из контекста боя
        items = fc.get("items", [])
        new_items = []
        for it in items:
            if it["id"] == item.item_id:
                if it["count"] > 1:
                    new_items.append({**it, "count": it["count"] - 1})
                # иначе — удаляем
            else:
                new_items.append(it)
        fc["items"] = new_items

    # атака монстра
    if fc["monster_hp"] > 0:
        m_dmg = calculate_monster_attack(monster) - user.defense
        m_dmg = max(1, m_dmg + fc["buffs"].get("defense", 0))
        fc["user_hp"] -= m_dmg
        msg += f"\nМонстр {fc['monster_name']} атакует: {m_dmg} урона."

    # завершение боя
    if fc["user_hp"] <= 0:
        user.energy -= 1
        user.abilities.pop("fight_context", None)
        flag_modified(user, "abilities")
        session.commit()
        return {"message": msg + "\n\nВы проиграли. Энергия -1"}

    if fc["monster_hp"] <= 0:
        gold = randint(10, 20)
        xp = randint(20, 30)
        user.gold += gold
        user.xp += xp
        user.energy -= 1

        # 📌 Обновление квеста, если он активен
        if user.active_quest_id:
            quest = session.query(Quest).get(user.active_quest_id)
            if quest.quest_type == "kill" and str(quest.target) == str(fc["monster_id"]):
                user.quest_progress += 1

                # 🎯 Если выполнен — выдаём награду
                if user.quest_progress >= quest.required:
                    user.gold += quest.reward_gold
                    user.xp += quest.reward_xp
                    if quest.reward_item_id:
                        inv = dict(user.inventory or {})
                        key = str(quest.reward_item_id)
                        inv[key] = inv.get(key, 0) + 1
                        user.inventory = inv
                        flag_modified(user, "inventory")

                    if not user.completed_quests:
                        user.completed_quests = []
                    user.completed_quests.append(quest.quest_id)
                    flag_modified(user, "completed_quests")

                    user.active_quest_id = None
                    user.quest_progress = 0

        user.abilities.pop("fight_context", None)
        flag_modified(user, "abilities")
        session.commit()

        return {
            "message": msg + f"\n\nВы победили! +{gold}💰, +{xp} XP.",
            "user_gold": user.gold,
            "user_xp": user.xp
        }


    # продолжаем бой
    fc["round"] += 1
    user.abilities["fight_context"] = fc.copy()
    flag_modified(user, "abilities")
    session.commit()

    return {
        "message": msg,
        "fight": fc,
        "round": fc["round"],
        "actions": ["attack", "flee", "useitem", "useskill"],
        "items": fc["items"],
        "skills": fc.get("skills", [])
    }
