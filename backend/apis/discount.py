from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timedelta
from threading import Timer

router = APIRouter()

class DiscountRequest(BaseModel):
    percent: float
    duration_days: int

active_discounts = []

def remove_discount(discount):
    active_discounts.remove(discount)

@router.post("/apply-discount")
def apply_discount(req: DiscountRequest):
    end_time = datetime.now() + timedelta(days=req.duration_days)
    discount = {
        "percent": req.percent,
        "valid_until": end_time.isoformat()
    }
    active_discounts.append(discount)

    # Schedule removal
    seconds = req.duration_days * 86400
    Timer(seconds, remove_discount, args=[discount]).start()

    return {
        "status": "applied",
        "discount": discount
    }

@router.get("/active-discounts")
def get_discounts():
    return {"discounts": active_discounts}
