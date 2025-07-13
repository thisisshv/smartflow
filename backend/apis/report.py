from fastapi import APIRouter

router = APIRouter()

# This would connect to real logs later
report_log = []

@router.get("/report")
def get_report():
    return {"log": report_log}

@router.post("/report")
def add_report(entry: dict):
    report_log.append(entry)
    return {"status": "logged", "entry": entry}
