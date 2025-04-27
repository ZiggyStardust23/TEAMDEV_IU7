
from fastapi import APIRouter
from back.schemas.start_schema import ChoseRequest, StartRequest
from back.services import start

router = APIRouter()

@router.post("/")
def create_user(req: StartRequest):
    return start.create_user(req.tg_id, req.username)

@router.post("/class")
def create_user(req: ChoseRequest):
    return start.choose_class(req.tg_id, req.chosen, req.username)
