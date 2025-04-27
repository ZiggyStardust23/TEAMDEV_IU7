
from fastapi import APIRouter
from back.schemas.fight_schema import FightStartRequest, FightActionRequest
from back.services import fight

router = APIRouter()

@router.post("/start")
def start_fight(req: FightStartRequest):
    return fight.fight_start(req.tg_id)

@router.post("/action")
def fight_action(req: FightActionRequest):
    return fight.fight_action(req.tg_id, req.action, req.skill_id, req.item_id)
