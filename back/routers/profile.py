
from fastapi import APIRouter
from schemas.profile_schema import ProfileRequest
from services import userProfile

router = APIRouter()

@router.post("/")
def get_profile(req: ProfileRequest):
    return userProfile.get_profile(req.tg_id)
