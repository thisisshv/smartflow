from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PriorityRequest(BaseModel):
    ticket_id: str
    class_type: str  # business/economy

@router.post("/priority-boarding")
def priority_boarding(req: PriorityRequest):
    if req.class_type.lower() != "business":
        return {"status": "denied", "reason": "only for business class"}
    return {
        "status": "granted",
        "ticket_id": req.ticket_id
    }
