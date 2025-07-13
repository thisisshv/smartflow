import json
from typing import Dict, Any
import os
from datetime import datetime

CONFIG_PATH = "business_rules.json"

# Default rules
default_rules = {
    "skip_steps": [],
    "force_steps": [],
    "tool_substitutions": {}
}

# Load or create config
def load_rules() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_rules, f)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_rules(rules: Dict[str, Any]):
    with open(CONFIG_PATH, "w") as f:
        json.dump(rules, f, indent=2)

def reset_rules():
    save_rules(default_rules)

def update_rules(updates: Dict[str, Any]):
    rules = load_rules()
    for key, value in updates.items():
        if isinstance(value, dict) and key in rules:
            rules[key].update(value)
        else:
            rules[key] = value
    save_rules(rules)

def cleanup_expired_rules():
    rules = load_rules()
    if "discount" in rules:
        if datetime.now().isoformat() > rules["discount"].get("expires_at", ""):
            rules["discount"]["enabled"] = False
            save_rules(rules)
