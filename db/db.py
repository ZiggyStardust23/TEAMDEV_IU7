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
    description = Column(String, nullable=False)
    type = Column(String(50), nullable=False)
    reward = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserQuest(Base):
    __tablename__ = 'UserQuests'
    user_id = Column(Integer, ForeignKey('Users.user_id'), primary_key=True)
    quest_id = Column(Integer, ForeignKey('Quests.quest_id'), primary_key=True)
    status = Column(String(50), default='active')
    progress = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

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