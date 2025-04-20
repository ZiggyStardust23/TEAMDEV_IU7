
from pydantic import BaseModel

class FightStartRequest(BaseModel):
    tg_id: str

class FightActionRequest(BaseModel):
    tg_id: str
    action: str
    skill_id: int | None = None
    item_id: int | None = None
