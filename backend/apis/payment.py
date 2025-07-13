from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PaymentRequest(BaseModel):
    ticket_id: str

@router.post("/process-payment")
def process_payment(payload: PaymentRequest):
    return {
        "status": "payment_success",
        "ticket_id": payload.ticket_id,
        "amount_charged": 999.0
    }
