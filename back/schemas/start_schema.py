
from pydantic import BaseModel

class StartRequest(BaseModel):
    tg_id: str
    username: str

class ChoseRequest(BaseModel):
    tg_id: str
    chosen: str
    username: str
