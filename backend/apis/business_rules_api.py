from fastapi import APIRouter
from backend.utils.business_rules import load_rules, update_rules, reset_rules

router = APIRouter()

@router.get("/rules")
def get_rules():
    return load_rules()

@router.post("/rules/update")
def set_rules(update: dict):
    update_rules(update)
    return {"status": "updated"}

@router.post("/rules/reset")
def reset():
    reset_rules()
    return {"status": "reset"}
