
from pydantic import BaseModel

class QuestActionRequest(BaseModel):
    tg_id: str
    action: str
    quest_id: int | None = None
