from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class RefundRequest(BaseModel):
    ticket_id: str

@router.post("/refund-status")
def refund_status(req: RefundRequest):
    status = random.choice(["processing", "refunded", "failed"])
    return {
        "ticket_id": req.ticket_id,
        "refund_status": status
    }
