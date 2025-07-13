from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class FlightSearchRequest(BaseModel):
    from_city: str
    to_city: str
    date: str

@router.post("/search-flights")
def search_flights(req: FlightSearchRequest):
    flights = [
        {"flight": "AI-101", "time": "10:00 AM"},
        {"flight": "SG-404", "time": "3:00 PM"},
        {"flight": "6E-666", "time": "8:30 PM"}
    ]
    return {
        "status": "success",
        "available_flights": random.sample(flights, k=2)
    }
