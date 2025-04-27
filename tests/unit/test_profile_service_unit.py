import unittest
from unittest.mock import patch, MagicMock
from back.services import userProfile

class ProfileServiceUnitTests(unittest.TestCase):

    @patch("back.services.userProfile.session")
    def test_get_profile_success(self, mock_session):
        user = MagicMock(
            username="Hero", class_="Warrior", level=5, xp=120, health=100,
            mana=50, attack=15, defense=10, gold=200, energy=5,
            inventory={}, active_quest_id=None
        )
        mock_session.query().filter_by().first.return_value = user
        result = userProfile.get_profile("user123")
        self.assertIn("👤 Профиль", result["message"])