from db import Skill, Item, Monster, Quest
from dbSession import session

mage_skills = [
    Skill(name="Огненный шар", type="damage", power=70, mana_cost=30),
    Skill(name="Ледяная тюрьма", type="damage", power=40, mana_cost=25),
    Skill(name="Энергетический всплеск", type="damage", power=90, mana_cost=50),
]
warrior_skills = [
    Skill(name="Разрубающий удар", type="damage", power=50, mana_cost=0),
    Skill(name="Берсерк", type="buff_attack", power=30, mana_cost=10),
    Skill(name="Землетрясение", type="damage", power=40, mana_cost=20),
]
archer_skills = [
    Skill(name="Снайперский выстрел", type="damage", power=65, mana_cost=15),
    Skill(name="Дождь стрел", type="damage", power=35, mana_cost=20),
    Skill(name="Ядовитая стрела", type="damage", power=25, mana_cost=10),
]

items = [
    Item(name="❤️ Зелье здоровья", type="heal", power=30, attack_bonus=0, defense_bonus=0, price=5),
    Item(name="💪 Камень силы", type="buff_attack", power=5, attack_bonus=0, defense_bonus=0, price=5),
    Item(name="💨 Дымовая шашка", type="escape", power=0, attack_bonus=0, defense_bonus=0, price=5),
]

monster = Monster(name="Goblin", level=3, health=11, attack=11, defense=4, gold_reward=12, xp_reward=12)
quest = Quest(name="Goblin Slayer", 
              description="Убить гоблинов", 
              quest_type="kill", 
              target="1", 
              required=3,
              reward_gold=11
              )

session.add_all(mage_skills + warrior_skills + archer_skills)
session.add_all(items)
session.add(monster)
session.add(quest)

session.commit()
session.close()