
from pydantic import BaseModel

class ProfileRequest(BaseModel):
    tg_id: str
