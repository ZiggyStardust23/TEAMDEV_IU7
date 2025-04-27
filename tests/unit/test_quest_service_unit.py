import unittest
from unittest.mock import MagicMock, patch
from back.services import quest

class QuestServiceUnitTests(unittest.TestCase):

    @patch("back.services.quest.session")
    def test_handle_quest_user_not_found(self, mock_session):
        mock_session.query().filter_by().first.return_value = None
        result = quest.handle_quest("user123", "current")
        self.assertEqual(result, {"error": "Сначала создайте персонажа."})

    @patch("back.services.quest.session")
    def test_handle_quest_accept_success(self, mock_session):
        user = MagicMock()
        mock_session.query().filter_by().first.return_value = user
        result = quest.handle_quest("user123", "accept", quest_id=1)
        self.assertEqual(result, {"message": "🎉 Квест принят!"})