from fastapi import FastAPI, Query
from backend.services.mistral_client import query_mistral
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

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Smartflow backend is running."}

@app.post("/execute")
async def run_command(command: str = Query(..., description="English command")):
    mistral_response_raw = query_mistral(command)

    print("\n--- MISTRAL RAW RESPONSE ---")
    print(mistral_response_raw)

    # Try to parse model output as JSON
    try:
        json_start = mistral_response_raw.find("{")
        parsed = json.loads(mistral_response_raw[json_start:])
    except Exception as e:
        return {
            "error": "Failed to parse LLM response",
            "details": str(e),
            "raw_response": mistral_response_raw
        }

    # If it's a rules update (rule keys present)
    if any(k in parsed for k in ["skip_steps", "force_steps", "tool_substitutions", "discount"]):
        try:
            update_rules(parsed)
            return {
                "status": "rules updated",
                "new_rules": load_rules(),
                "raw_response": mistral_response_raw
            }
        except Exception as e:
            return {
                "error": "Failed to update rules",
                "details": str(e),
                "raw_response": mistral_response_raw
            }

    # Otherwise, treat it as workflow intent
    try:
        # Convert to IntentResponse model
        if "tools" in parsed:
            parsed["actions"] = [
                {"tool": tool["name"], "params": tool["parameters"]}
                for tool in parsed["tools"]
            ]
            del parsed["tools"]

        intent_data = IntentResponse(**parsed)
        result = await execute_workflow(intent_data)
        result["raw_response"] = mistral_response_raw
        return result

    except Exception as e:
        return {
            "error": "Failed to execute workflow",
            "details": str(e),
            "raw_response": mistral_response_raw
        }

@app.post("/update-rules")
async def update_business_rules(payload: dict):
    try:
        update_rules(payload)
        return load_rules()
    except Exception as e:
        return {"error": str(e)}

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
