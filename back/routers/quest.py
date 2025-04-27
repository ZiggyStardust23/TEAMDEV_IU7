
from fastapi import APIRouter
from back.schemas.quest_schema import QuestActionRequest
from back.services import quest

router = APIRouter()

@router.post("/")
def handle_quest(req: QuestActionRequest):
    return quest.handle_quest(req.tg_id, req.action, req.quest_id)
