tickets_db = {}  # ticket_id -> ticket info
ticket_status = {}  # ticket_id -> status

customers_db = {}  # traveler_name or ID -> info

def add_ticket(ticket_id: str, data: dict):
    tickets_db[ticket_id] = data
    ticket_status[ticket_id] = "booked"

def get_ticket(ticket_id: str):
    return tickets_db.get(ticket_id)

def update_ticket(ticket_id: str, updates: dict):
    if ticket_id in tickets_db:
        tickets_db[ticket_id].update(updates)
        return tickets_db[ticket_id]
    return None

def cancel_ticket(ticket_id: str, reason: str):
    if ticket_id in ticket_status:
        ticket_status[ticket_id] = f"cancelled: {reason}"
        return True
    return False

def get_ticket_status(ticket_id: str):
    return ticket_status.get(ticket_id, "not_found")
