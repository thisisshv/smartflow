from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class MealRequest(BaseModel):
    ticket_id: str
    meal_type: str  # veg/non-veg/jain etc.

@router.post("/meal-preference")
def meal_preference(req: MealRequest):
    return {
        "status": "recorded",
        "ticket_id": req.ticket_id,
        "meal_type": req.meal_type
    }
