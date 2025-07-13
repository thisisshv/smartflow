from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UpdateInfo(BaseModel):
    ticket_id: str
    traveler_name: str
    contact: str

@router.post("/update-info")
def update_info(req: UpdateInfo):
    return {
        "status": "updated",
        "ticket_id": req.ticket_id,
        "new_info": {
            "name": req.traveler_name,
            "contact": req.contact
        }
    }
