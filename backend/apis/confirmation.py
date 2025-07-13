from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class ConfirmRequest(BaseModel):
    ticket_id: str
    traveler_name: str

@router.post("/confirm-ticket")
def confirm(req: ConfirmRequest):
    if random.random() < 0.2:
        return {"status": "failure", "reason": "Traveler info mismatch"}
    
    return {"status": "confirmed", "ticket_id": req.ticket_id}
