import os
from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from back.db.db import Base
import back.db.dbSession as dbSession
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
load_dotenv()
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_NAME = "telegram_bot_test"
DB_USER = os.getenv("POSTGRES_USER", "botuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "botpassword")


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("DATABASE_URI =", DATABASE_URL)

def create_test_db():
    connection = psycopg2.connect(
        dbname="postgres", user="botuser", password="botpassword", host="postgres"
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'telegram_bot_test'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute('CREATE DATABASE telegram_bot_test')
    cursor.close()
    connection.close()

create_test_db()

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    """Создание таблиц в тестовой базе перед всеми тестами"""
    Base.metadata.drop_all(bind=engine)  # Очищаем всё перед тестами
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_database, monkeypatch):
    """Создание тестовой сессии для каждого теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # ПОДМЕНЯЕМ dbSession.session на ТЕСТОВЫЙ
    monkeypatch.setattr(dbSession, "session", session)

    # ПОДМЕНЯЕМ session в сервисах
    import back.services.fight as fight_service
    import back.services.quest as quest_service
    import back.services.shop as shop_service
    import back.services.start as start_service
    import back.services.userProfile as profile_service

    fight_service.session = session
    quest_service.session = session
    shop_service.session = session
    start_service.session = session
    profile_service.session = session

    yield session

    transaction.rollback()
    connection.close()
