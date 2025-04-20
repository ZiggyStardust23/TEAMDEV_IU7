
from fastapi import APIRouter
from schemas.start_schema import StartRequest
from services import start

router = APIRouter()

@router.post("/")
def create_user(req: StartRequest):
    return start.create_user(req.tg_id, req.username)
