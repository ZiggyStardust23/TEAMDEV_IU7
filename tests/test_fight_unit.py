import pytest
from unittest.mock import MagicMock, patch
from commands.fight import (
    calculate_user_attack,
    calculate_monster_attack,
    apply_item_effect,
    apply_skill_effect,
    get_random_monster,
)
from db.db import User, Monster

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.attack = 10
    user.defense = 5
    user.health = 100
    user.mana = 50
    user.level = 1
    return user

@pytest.fixture
def mock_monster():
    monster = MagicMock(spec=Monster)
    monster.attack = 8
    monster.defense = 3
    monster.health = 50
    monster.name = "Гоблин"
    return monster

@pytest.fixture
def mock_fight_context():
    return {
        "user_hp": 50,
        "monster_hp": 50,
        "buffs": {"attack": 0, "defense": 0}
    }

def test_calculate_user_attack(mock_user):
    assert calculate_user_attack(mock_user) == 10
    assert calculate_user_attack(mock_user, 5) == 15

def test_calculate_monster_attack(mock_monster):
    with patch('random.randint', return_value=0):
        assert calculate_monster_attack(mock_monster) == 8

def test_apply_item_effect_heal(mock_user, mock_fight_context):
    item = {"type": "heal", "power": 20, "name": "Зелье здоровья"}
    effect_message = apply_item_effect(mock_user, item, mock_fight_context)
    assert mock_fight_context["user_hp"] == 70
    assert "Восстановлено 20 здоровья" in effect_message

def test_apply_skill_effect_damage(mock_user, mock_fight_context):
    skill = {"type": "damage", "power": 15, "name": "Огненный шар"}
    effect_message = apply_skill_effect(mock_user, skill, mock_fight_context)
    assert mock_fight_context["monster_hp"] == 35
    assert "Нанесено 15.0 магического урона" in effect_message

@patch('random.choice')
def test_get_random_monster(mock_choice, mock_monster):
    mock_choice.return_value = mock_monster
    monster = get_random_monster()
    assert monster.name == "Гоблин"