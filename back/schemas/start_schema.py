
from pydantic import BaseModel

class StartRequest(BaseModel):
    tg_id: str
    username: str
