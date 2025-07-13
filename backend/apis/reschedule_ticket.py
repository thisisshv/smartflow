from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RescheduleRequest(BaseModel):
    ticket_id: str
    new_date: str

@router.post("/reschedule-ticket")
def reschedule(req: RescheduleRequest):
    return {
        "status": "rescheduled",
        "ticket_id": req.ticket_id,
        "new_date": req.new_date
    }
