from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.services.cohere_client import cohere_to_structured_json
from backend.services.workflow_manager import execute_workflow
from backend.utils.models import IntentResponse
from backend.utils.business_rules import load_rules, update_rules
from backend.apis import (
    book_ticket, search_flights, payment, email, confirmation, report,
    contact_customer, discount,
    cancel_ticket, update_traveler_info, add_travel_insurance,
    frequent_flyer_rewards, priority_boarding, seat_selection,
    baggage_upgrade, meal_preference, reschedule_ticket, refund_status,
    business_rules_api
)
import json
import re

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Smartflow backend is running."}

@app.post("/execute")
async def run_command(command: str = Query(..., description="English command")):
    # Use Cohere to extract intent and structure it into JSON
    structured = cohere_to_structured_json(command)
    print("\n--- STRUCTURED INTENT ---")
    print(structured)
    parsed = structured

    # If it's a rules update (rule keys present)
    if any(k in parsed for k in ["skip_steps", "force_steps", "tool_substitutions", "discount"]):
        try:
            update_rules(parsed)
            return {
                "status": "rules updated",
                "new_rules": load_rules(),
                "raw_response": parsed
            }
        except Exception as e:
            return {
                "error": "Failed to update rules",
                "details": str(e),
                "raw_response": parsed
            }

    # Otherwise, treat it as workflow intent
    try:
        if "tools" in parsed:
            parsed["actions"] = [
                {"tool": tool["name"], "params": tool["parameters"]}
                for tool in parsed["tools"]
            ]
            del parsed["tools"]

        intent_data = IntentResponse(**parsed)
        result = await execute_workflow(intent_data)
        result["raw_response"] = parsed
        return result
    except Exception as e:
        return {
            "error": "Failed to execute workflow",
            "details": str(e),
            "raw_response": parsed
        }

@app.post("/update-rules")
async def update_business_rules(payload: dict):
    try:
        update_rules(payload)
        return load_rules()
    except Exception as e:
        return {"error": str(e)}

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()},
    )

# ✅ Register all tool routers
routers = [
    book_ticket.router, search_flights.router, payment.router, email.router,
    confirmation.router, report.router, contact_customer.router, discount.router,
    cancel_ticket.router, update_traveler_info.router, add_travel_insurance.router,
    frequent_flyer_rewards.router, priority_boarding.router, seat_selection.router,
    baggage_upgrade.router, meal_preference.router, reschedule_ticket.router,
    refund_status.router, business_rules_api.router
]

for router in routers:
    app.include_router(router)
