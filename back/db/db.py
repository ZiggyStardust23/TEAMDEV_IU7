from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

def init_data():
# Проверяем таблицы
    skills_exist = session.query(Skill).first()
    items_exist = session.query(Item).first()
    monsters_exist = session.query(Monster).first()
    quests_exist = session.query(Quest).first()

    # Навыки
    if not skills_exist:
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
        session.add_all(mage_skills + warrior_skills + archer_skills)

    # Предметы
    if not items_exist:
        items = [
            Item(name="❤️ Зелье здоровья", type="heal", power=30, attack_bonus=0, defense_bonus=0, price=5),
            Item(name="💪 Камень силы", type="buff_attack", power=5, attack_bonus=0, defense_bonus=0, price=5),
            Item(name="💨 Дымовая шашка", type="escape", power=0, attack_bonus=0, defense_bonus=0, price=5),
        ]
        new_items = [
            Item(name="⚡️ Молниеносное зелье", type="buff_attack", power=10, attack_bonus=0, defense_bonus=0, price=10),
            Item(name="🛡 Кольцо защиты", type="buff_defense", power=5, attack_bonus=0, defense_bonus=5, price=8),
            Item(name="🔥 Зелье ярости", type="buff_attack", power=15, attack_bonus=0, defense_bonus=0, price=12),
            Item(name="🍀 Амулет удачи", type="buff_attack", power=7, attack_bonus=0, defense_bonus=2, price=9),
            Item(name="🧪 Большое зелье здоровья", type="heal", power=70, attack_bonus=0, defense_bonus=0, price=15),
            Item(name="🎯 Лук мастера", type="buff_attack", power=20, attack_bonus=5, defense_bonus=0, price=20),
        ]
        session.add_all(items + new_items)

    # Монстры
    if not monsters_exist:
        base_monster = Monster(name="Goblin", level=3, health=11, attack=11, defense=4, gold_reward=12, xp_reward=12)
        monsters = [
            Monster(name="Orc", level=5, health=20, attack=15, defense=5, gold_reward=20, xp_reward=25),
            Monster(name="Skeleton", level=7, health=25, attack=18, defense=6, gold_reward=25, xp_reward=30),
            Monster(name="Dark Mage", level=10, health=35, attack=22, defense=8, gold_reward=35, xp_reward=40),
            Monster(name="Wolf", level=4, health=15, attack=13, defense=4, gold_reward=18, xp_reward=20),
            Monster(name="Dragonling", level=12, health=50, attack=30, defense=10, gold_reward=50, xp_reward=60),
        ]
        session.add_all([base_monster] + monsters)

    # Квесты
    if not quests_exist:
        base_quest = Quest(name="Goblin Slayer", description="Убить гоблинов", quest_type="kill", target="1", required=3, reward_gold=11)
        quests = [
            Quest(name="Orc Hunt", description="Убейте орков", quest_type="kill", target="2", required=3, reward_gold=20, reward_xp=25),
            Quest(name="Skeleton Bane", description="Убейте скелетов", quest_type="kill", target="3", required=2, reward_gold=25, reward_xp=30),
            Quest(name="Dark Mage Slayer", description="Победите тёмных магов", quest_type="kill", target="4", required=1, reward_gold=35, reward_xp=40),
            Quest(name="Wolf Extermination", description="Убейте волков", quest_type="kill", target="5", required=4, reward_gold=18, reward_xp=20),
            Quest(name="Dragonling Conqueror", description="Уничтожьте детёнышей драконов", quest_type="kill", target="6", required=1, reward_gold=50, reward_xp=60),
        ]
        session.add_all([base_quest] + quests)

    session.commit()
    session.close()


load_dotenv()
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_NAME = os.getenv("POSTGRES_DB", "telegram_bot")
DB_USER = os.getenv("POSTGRES_USER", "botuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "botpassword")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("DATABASE_URI =", DATABASE_URL)
engine = create_engine(DATABASE_URL)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    class_ = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    health = Column(Integer, default=100)
    mana = Column(Integer, default=50)
    attack = Column(Integer, default=10)
    defense = Column(Integer, default=5)
    gold = Column(Integer, default=0)
    energy = Column(Integer, default=10)
    abilities = Column(JSON)
    inventory = Column(JSON)
    active_quest_id = Column(Integer, ForeignKey('Quests.quest_id'))
    quest_progress = Column(Integer, default=0)
    completed_quests = Column(JSON, default=list)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Monster(Base):
    __tablename__ = 'Monsters'
    monster_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    health = Column(Integer, default=50)
    attack = Column(Integer, default=5)
    defense = Column(Integer, default=2)
    gold_reward = Column(Integer, default=10)
    xp_reward = Column(Integer, default=20)
    abilities = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Item(Base):
    __tablename__ = 'Items'
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    power = Column(Integer, default=0)
    attack_bonus = Column(Integer, default=0)
    defense_bonus = Column(Integer, default=0)
    effect = Column(String(100))
    price = Column(Integer, default=0)
    rarity = Column(String(50), default='common')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Skill(Base):
    __tablename__ = 'Skills'
    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    power = Column(Integer, default=0)
    mana_cost = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Quest(Base):
    __tablename__ = 'Quests'
    quest_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    quest_type = Column(String(50))
    target = Column(String(50))      
    required = Column(Integer)       
    reward_gold = Column(Integer)
    reward_xp = Column(Integer)
    reward_item_id = Column(Integer, ForeignKey('Items.item_id'))
    min_level = Column(Integer, default=1)

class Battle(Base):
    __tablename__ = 'Battles'
    battle_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    monster_id = Column(Integer, ForeignKey('Monsters.monster_id'))
    result = Column(String(50), nullable=False)
    reward = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

Base.metadata.create_all(engine)

init_data()
print("Таблицы успешно созданы!")