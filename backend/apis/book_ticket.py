from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class TicketRequest(BaseModel):
    from_city: str
    to_city: str
    date: str
    traveler_name: str

@router.post("/book-ticket")
def book_ticket(req: TicketRequest):
    ticket_id = f"TKT{random.randint(1000,9999)}"
    return {
        "status": "success",
        "ticket_id": ticket_id,
        "details": req
    }
