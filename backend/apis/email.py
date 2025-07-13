from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@router.post("/send-email")
def send_email(req: EmailRequest):
    return {
        "status": "sent",
        "to": req.to,
        "subject": req.subject
    }
