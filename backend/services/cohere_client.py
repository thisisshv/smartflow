import cohere
import os
import re
import json

# Use the Cohere API key from environment variable
CO_API_KEY = os.environ.get("CO_API_KEY")
if not CO_API_KEY:
    raise RuntimeError("CO_API_KEY environment variable not set. Please set your Cohere API key.")

co = cohere.Client(CO_API_KEY)

# Prompt to guide LLM for interpreting commands
COHERE_PROMPT = """
You are a backend configuration assistant for a smart ticket booking system. You will receive natural language commands from a business user and must convert them into structured JSON that modifies business rules or workflows. Your job is to interpret these instructions into one or more of the following fields:

{
  "skip_steps": [],  // list of tools to skip (like "send_email", "process_payment", "cancel_ticket")
  "force_steps": [], // list of tools to always run regardless of other conditions
  "tool_substitutions": {}, // optional substitution of tool names
  "discount": {
    "enabled": true,
    "amount_percent": 20,
    "expires_at": "2025-08-31T23:59:59"
  }
}

💡 You must:
- Parse user intent correctly even if phrased informally (e.g. “remove email,” “don’t send confirmation,” “allow skipping payments”).
- Support rules like: skip/force steps, enable/disable tools, set discount % and expiry in ISO format.
- Recognize synonyms: e.g. “confirmation mail” → `send_email`, “payment required” → `process_payment`
- Default discount expiry to 7 days from now if not specified.
- Return only one top-level JSON object as output. Never explain anything.

Examples:
---
Input: “Book tickets directly without needing to pay.”
Output:
{
  "skip_steps": ["process_payment"]
}

Input: “Apply a 15% discount until end of this month”
Output:
{
  "discount": {
    "enabled": true,
    "amount_percent": 15,
    "expires_at": "2025-07-31T23:59:59"
  }
}

Input: “Stop sending confirmation emails”
Output:
{
  "skip_steps": ["send_email"]
}

Input: “Always apply priority boarding and contact the customer”
Output:
{
  "force_steps": ["priority_boarding", "contact_customer"]
}

Input: “Remove all current rules and disable discounts”
Output:
{
  "skip_steps": [],
  "force_steps": [],
  "tool_substitutions": {},
  "discount": {
    "enabled": false,
    "amount_percent": 0,
    "expires_at": "2025-01-01T00:00:00"
  }
}
"""

def query_cohere(prompt: str) -> str:
    response = co.chat(
        model="command-r-plus-08-2024",  # Or use os.environ.get("COHERE_MODEL")
        message=prompt,
        preamble=COHERE_PROMPT,
        max_tokens=512,
        temperature=0.3,
    )
    # Always return a string, fallback to str(response) if .text is missing
    return response.text.strip() if hasattr(response, "text") else str(response).strip()

COHERE_PREAMBLE = "You are an assistant that summarizes user workflow commands in plain English."

# Use Cohere to get a plain English summary or intent

def get_intent_from_cohere(prompt: str) -> str:
    response = co.chat(
        model="command-r-plus-08-2024",
        message=prompt,
        preamble=COHERE_PREAMBLE,
        max_tokens=100,
        temperature=0.3,
    )
    return response.text.strip()

# Use Python to structure the output into JSON

def structure_intent_to_json(intent: str) -> dict:
    # Match 'skip ...', 'remove ... step', or 'remove ...'
    skip_match = re.search(r"(?:skip|remove)(?: the)? ([a-zA-Z_ ]+?)(?: step)?$", intent, re.IGNORECASE)
    if skip_match:
        tool = skip_match.group(1).strip().replace(" ", "_")
        return {"skip_steps": [tool]}
    # Add more parsing/classification logic as needed
    return {"unparsed_intent": intent}

# Example utility to go from user input to structured JSON

def cohere_to_structured_json(user_input: str) -> dict:
    response = query_cohere(user_input)
    try:
        return json.loads(response)
    except Exception:
        # Fallback: try to parse with regex if not valid JSON
        return structure_intent_to_json(response)

    