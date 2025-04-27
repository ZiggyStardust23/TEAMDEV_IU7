
from pydantic import BaseModel

class BuyRequest(BaseModel):
    tg_id: str
    item_id: int

class ItemsRequest(BaseModel):
    tg_id: str