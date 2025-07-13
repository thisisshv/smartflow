from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SeatRequest(BaseModel):
    ticket_id: str
    seat_number: str

@router.post("/select-seat")
def select_seat(req: SeatRequest):
    return {
        "status": "seat_selected",
        "ticket_id": req.ticket_id,
        "seat": req.seat_number
    }
