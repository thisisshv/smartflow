from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CancelRequest(BaseModel):
    ticket_id: str
    reason: str

@router.post("/cancel-ticket")
def cancel_ticket(req: CancelRequest):
    return {
        "status": "cancelled",
        "ticket_id": req.ticket_id,
        "reason": req.reason
    }
