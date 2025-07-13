from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ContactRequest(BaseModel):
    name: str
    reason: str
    ticket_id: str

@router.post("/contact-customer")
def contact_customer(req: ContactRequest):
    return {
        "status": "notified",
        "message": f"Customer {req.name} was notified about: {req.reason}"
    }
