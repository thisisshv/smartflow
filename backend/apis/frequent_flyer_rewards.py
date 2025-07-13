from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RewardRequest(BaseModel):
    traveler_id: str
    ticket_id: str

@router.post("/apply-rewards")
def apply_rewards(req: RewardRequest):
    return {
        "status": "rewards_applied",
        "traveler_id": req.traveler_id,
        "ticket_id": req.ticket_id
    }
