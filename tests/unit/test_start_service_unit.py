import unittest
from unittest.mock import patch, MagicMock
from back.services import start

class StartServiceUnitTests(unittest.TestCase):

    @patch("back.services.start.session")
    def test_create_user_already_exists(self, mock_session):
        mock_session.query().filter_by().first.return_value = MagicMock()
        result = start.create_user("user123", "name")
        self.assertEqual(result, {"message": "Вы уже создали персонажа."})

    def test_choose_class_invalid(self):
        result = start.choose_class("user123", "invalid", "TestUser")
        self.assertEqual(result, {"error": "Неверный класс"})

    @patch("back.services.start.session")
    def test_choose_class_success(self, mock_session):
        mock_session.query().filter_by().first.return_value = None
        result = start.choose_class("tg123", "mage", "TestUser")
        self.assertTrue(result["message"].startswith("Вы выбрали класс Mage"))