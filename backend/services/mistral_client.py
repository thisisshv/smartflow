import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
API_URL = os.getenv("OPENROUTER_API")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Prompt to guide LLM for interpreting commands
MISTRAL_PROMPT = """
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

def query_mistral(prompt: str) -> str:
    print(f"[DEBUG] Prompt: {prompt}")
    print("[DEBUG] API_KEY:", API_KEY)
    print("[DEBUG] MODEL_NAME:", MODEL_NAME)
    print("[DEBUG] OPENROUTER_API:", API_URL)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": MISTRAL_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.3,
        "top_p": 0.95
    }

    response = requests.post(f"{API_URL}/chat/completions", headers=HEADERS, json=payload)

    try:
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] OpenRouter error: {e}, {response.text}")
        raise RuntimeError(f"OpenRouter error: {response.status_code}, {response.text}")

    result = response.json()
    content = result["choices"][0]["message"]["content"]
    print(f"[DEBUG] Response: {content}")
    return content.strip()
