from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BaggageRequest(BaseModel):
    ticket_id: str
    extra_kg: int

@router.post("/baggage-upgrade")
def baggage_upgrade(req: BaggageRequest):
    return {
        "status": "upgraded",
        "ticket_id": req.ticket_id,
        "extra_kg": req.extra_kg
    }
