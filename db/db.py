from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI)
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
    completed_quests = Column(JSON, default=list)  # Список завершенных квестов
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

class Quest(Base):
    __tablename__ = 'Quests'
    quest_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300))
    quest_type = Column(String(50))  # 'kill', 'collect', 'explore'
    target = Column(String(50))      # 'monster_id' или 'item_id'
    required = Column(Integer)       # Сколько нужно
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

print("Таблицы успешно созданы!")