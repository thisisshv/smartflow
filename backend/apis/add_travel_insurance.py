from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class InsuranceRequest(BaseModel):
    ticket_id: str
    plan: str

@router.post("/add-insurance")
def add_insurance(req: InsuranceRequest):
    return {
        "status": "insurance_added",
        "ticket_id": req.ticket_id,
        "plan": req.plan
    }
