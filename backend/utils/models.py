from pydantic import BaseModel
from typing import List, Dict

class Action(BaseModel):
    tool: str
    params: Dict[str, str]

class IntentResponse(BaseModel):
    intent: str
    actions: List[Action]
