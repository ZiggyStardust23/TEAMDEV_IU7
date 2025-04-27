import unittest
from unittest.mock import MagicMock, patch
from back.services import fight

class FightServiceUnitTests(unittest.TestCase):

    @patch("back.services.fight.session")
    def test_fight_start_user_not_found(self, mock_session):
        mock_session.query().filter_by().first.return_value = None
        result = fight.fight_start("user123")
        self.assertEqual(result, {"error": "Сначала создайте персонажа."})

    @patch("back.services.fight.get_random_monster")
    @patch("back.services.fight.session")
    def test_fight_start_success(self, mock_session, mock_monster):
        user = MagicMock()
        user.energy = 5
        user.inventory = {}
        user.abilities = {"skills": []}
        user.health = 100
        user.mana = 50
        mock_session.query().filter_by().first.return_value = user
        monster_mock = MagicMock()
        monster_mock.monster_id = 1
        monster_mock.name = "Goblin"
        monster_mock.health = 50
        mock_monster.return_value = monster_mock
        result = fight.fight_start("user123")
        self.assertIn("fight", result)
        self.assertEqual(result["fight"]["monster_name"], "Goblin")