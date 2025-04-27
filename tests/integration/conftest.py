import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from back.db.db import Base
import back.db.dbSession as dbSession

# Подключение к тестовой БД PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:3259@localhost:5433/tests"
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
