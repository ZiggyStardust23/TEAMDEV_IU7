import unittest
from unittest.mock import MagicMock, patch
from back.services import shop

class ShopServiceUnitTests(unittest.TestCase):

    @patch("back.services.shop.session")
    def test_get_shop_items_success(self, mock_session):
        user = MagicMock(gold=100)
        item = MagicMock()
        item.item_id = 1
        item.name = "Potion"
        item.price = 10
        mock_session.query().filter_by().first.return_value = user
        mock_session.query().filter().order_by().all.return_value = [item]
        result = shop.get_shop_items("user123")
        self.assertEqual(result["user_gold"], 100)
        self.assertEqual(result["items"][0]["name"], "Potion")