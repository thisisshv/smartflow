import httpx
import json
from typing import Dict, Any
from backend.utils.models import IntentResponse, Action
from backend.utils.business_rules import load_rules

TOOL_ENDPOINTS = {
    "book_ticket": "/book-ticket",
    "search_flights": "/search-flights",
    "payment": "/payment",
    "send_email": "/send-email",
    "confirm_ticket": "/confirm-ticket",
    "report": "/report",
    "contact_customer": "/contact-customer",
    "apply_discount": "/apply-discount",
    "cancel_ticket": "/cancel-ticket",
    "update_info": "/update-info",
    "add_insurance": "/add-insurance",
    "apply_rewards": "/apply-rewards",
    "priority_boarding": "/priority-boarding",
    "select_seat": "/select-seat",
    "baggage_upgrade": "/baggage-upgrade",
    "meal_preference": "/meal-preference",
    "reschedule_ticket": "/reschedule-ticket",
    "refund_status": "/refund-status",
}

BASE_URL = "http://localhost:8000"

PARAMETER_MAPPING = {
    "book_ticket": {
        "from": "from_city",
        "to": "to_city",
        "passenger": "traveler_name",
    }
    # Add more tool-specific param maps here if needed
}

async def execute_workflow(intent_response: IntentResponse) -> Dict[str, Any]:
    results = []
    async with httpx.AsyncClient() as client:
        rules = load_rules()
        skip_steps = set(rules.get("skip_steps", []))
        force_steps = set(rules.get("force_steps", []))
        tool_subs = rules.get("tool_substitutions", {})

        filtered_actions = []
        for action in intent_response.actions:
            tool = action.tool
            if tool in skip_steps:
                result = {
                    "tool": tool,
                    "status": "skipped_by_rule",
                    "reason": "Skipped as per business rules"
                }
                results.append(result)
                # Log skipped step
                await client.post(f"{BASE_URL}/report", json=result)
                continue

            if tool in tool_subs:
                action.tool = tool_subs[tool]

            # Apply parameter mapping
            param_map = PARAMETER_MAPPING.get(tool, {})
            mapped_params = {param_map.get(k, k): v for k, v in action.params.items()}
            action.params = mapped_params

            filtered_actions.append(action)

        for forced_tool in force_steps:
            if all(a.tool != forced_tool for a in filtered_actions):
                filtered_actions.append(Action(tool=forced_tool, params={}))

        for action in filtered_actions:
            tool = action.tool
            params = action.params
            endpoint = TOOL_ENDPOINTS.get(tool)

            if not endpoint:
                result = {
                    "tool": tool,
                    "status": "error",
                    "message": f"Unknown tool '{tool}'"
                }
                results.append(result)
                # Log unknown tool
                await client.post(f"{BASE_URL}/report", json=result)
                continue

            try:
                response = await client.post(f"{BASE_URL}{endpoint}", json=params)
                response_data = response.json()
                result = {
                    "tool": tool,
                    "status": "success" if response.status_code == 200 else "failed",
                    "response": response_data
                }
                results.append(result)

                # Log successful/failure step
                await client.post(f"{BASE_URL}/report", json={
                    "tool": tool,
                    "status": result["status"],
                    "params": params,
                    "response": response_data
                })

            except Exception as e:
                result = {
                    "tool": tool,
                    "status": "exception",
                    "message": str(e)
                }
                results.append(result)

                # Log exception step
                await client.post(f"{BASE_URL}/report", json=result)

    return {
        "intent": intent_response.intent,
        "steps": results
    }
