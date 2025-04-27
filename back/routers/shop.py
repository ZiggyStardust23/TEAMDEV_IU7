
from fastapi import APIRouter
from back.schemas.shop_schema import BuyRequest, ItemsRequest
from back.services import shop

router = APIRouter()

@router.post("/buy")
def buy(req: BuyRequest):
    return shop.buy_item(req.tg_id, req.item_id)

@router.post("/items")
def buy(req: ItemsRequest):
    return shop.get_shop_items(req.tg_id)
