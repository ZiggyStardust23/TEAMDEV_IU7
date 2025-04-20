
from fastapi import APIRouter
from schemas.quest_schema import QuestActionRequest
from services import quest

router = APIRouter()

@router.post("/")
def handle_quest(req: QuestActionRequest):
    return quest.handle_quest(req.tg_id, req.action, req.quest_id)
