import streamlit as st
import requests
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000"  # or your deployed API URL

st.set_page_config(page_title="🎟️ Book Your Flight", layout="wide")

st.title("🎟️ Smart Ticket Booking Portal")

# --- Rules State Management ---
def fetch_rules():
    resp = requests.get(f"{BASE_URL}/rules")
    try:
        return resp.json()
    except ValueError:
        st.error("❌ Could not parse rules. Raw response:")
        st.code(resp.text)
        return {}

if "rules" not in st.session_state:
    st.session_state["rules"] = fetch_rules()

rules = st.session_state["rules"]
skip_steps = set(rules.get("skip_steps", []))
force_steps = set(rules.get("force_steps", []))
substitutions = rules.get("tool_substitutions", {})
discount_config = rules.get("discount", {})

# Sidebar Reports and Refresh
with st.sidebar:
    st.header("📊 Booking Reports")
    if st.button("📝 View All Bookings"):
        res = requests.get(f"{BASE_URL}/report")
        try:
            st.json(res.json())
        except ValueError:
            st.error("❌ Could not parse bookings. Raw response:")
            st.code(res.text)
    if st.button("🔄 Refresh Rules"):
        st.session_state["rules"] = fetch_rules()
        st.rerun()

# --- After any admin action, re-fetch rules ---
def update_rules_state():
    st.session_state["rules"] = fetch_rules()
    st.rerun()

# --- Active Discount Notice ---
discount_config = st.session_state["rules"].get("discount", {})
if discount_config.get("enabled"):
    percent = discount_config.get("amount_percent")
    expiry = discount_config.get("expires_at")
    st.markdown(f"### 🎉 {percent}% discount active until {expiry}")

def show_response(resp, action_desc="Action"):
    status = resp.get("status", "")
    if status in [
        "success", "upgraded", "confirmed", "sent", "recorded",
        "rescheduled", "insurance_added", "rewards_applied",
        "seat_selected", "payment_success", "cancelled", "notified", "refunded"
    ]:
        st.success(f"✅ {action_desc} succeeded.")
        st.json(resp)
    elif status == "skipped by rule" or status == "skipped_by_rule":
        st.info(f"ℹ️ {action_desc} was skipped due to business rules.")
    elif status == "denied":
        st.warning(f"⚠️ {action_desc} denied: {resp.get('reason', '')}")
    elif status == "failure":
        st.error(f"❌ {action_desc} failed: {resp.get('reason', '')}")
    elif status == "error" or status == "exception" or "error" in resp:
        st.error(f"❌ {action_desc} error: {resp.get('message', resp.get('error', 'Unknown error'))}")
        st.json(resp)
    else:
        st.warning(f"⚠️ {action_desc} returned unexpected status: {status}")
        st.json(resp)

def call_tool(tool_name, payload):
    actual_tool = substitutions.get(tool_name, tool_name)
    if actual_tool in skip_steps:
        return {"status": "skipped by rule"}
    try:
        response = requests.post(f"{BASE_URL}/{actual_tool.replace('_', '-')}", json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "error": "Connection failed - is the backend running?"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# --- Search Flights ---
if "search_flights" not in skip_steps:
    st.subheader("🔍 Search Flights")
    with st.form("search_form"):
        src = st.text_input("From", "Delhi")
        dest = st.text_input("To", "Goa")
        srch_date = st.date_input("Date", date.today())
        if st.form_submit_button("Search"):
            flights = call_tool("search_flights", {"from_city": src, "to_city": dest, "date": str(srch_date)})
            st.write("Available Flights")
            st.json(flights)

# --- Booking Form ---
ticket_id = None
if "book_ticket" not in skip_steps:
    st.subheader("✈️ Booking Form")
    with st.form("booking_form"):
        from_city = st.text_input("From City *", "Delhi")
        to_city = st.text_input("To City *", "Goa")
        travel_date = st.date_input("Travel Date *", date.today())
        traveler_name = st.text_input("Traveler Name *", "Shivanshu")
        seat = st.text_input("Preferred Seat", "")
        baggage_kg = st.slider("Extra Baggage (kg)", 0, 30, 0)
        insurance_plan = st.selectbox("Travel Insurance", ["None", "Basic", "Premium"])
        class_type = st.selectbox("Class Type", ["economy", "business"])
        discounts = ["None"]
        if discount_config.get("enabled"):
            discounts.append(f"AUTO-{discount_config.get('amount_percent')}%")
        selected_discount = st.selectbox("Apply Discount", discounts)
        ff_rewards = st.checkbox("Frequent Flyer Rewards")
        contact_cust = st.checkbox("Contact Customer")
        priority = st.checkbox("Priority Boarding")

        if st.form_submit_button("🚀 Book Ticket"):
            # Handle date input which returns a tuple
            if isinstance(travel_date, tuple) and len(travel_date) > 0:
                travel_date_str = travel_date[0].isoformat()
            else:
                travel_date_str = str(travel_date)
            ticket_resp = call_tool("book_ticket", {
                "from_city": from_city,
                "to_city": to_city,
                "date": travel_date_str,
                "traveler_name": traveler_name
            })
            ticket_id = ticket_resp.get("ticket_id")
            if ticket_id:
                st.success(f"🎫 Ticket ID: {ticket_id}")
            else:
                st.error("❌ Failed to book ticket.")
            st.json(ticket_resp)

            if ticket_id:
                if baggage_kg > 0 and "baggage_upgrade" not in skip_steps:
                    resp = call_tool("baggage_upgrade", {"ticket_id": ticket_id, "extra_kg": baggage_kg})
                    show_response(resp, "Baggage Upgrade")

                if seat and "select_seat" not in skip_steps:
                    resp = call_tool("select_seat", {"ticket_id": ticket_id, "seat_number": seat})
                    show_response(resp, "Seat Selection")

                if insurance_plan != "None" and "add_insurance" not in skip_steps:
                    resp = call_tool("add_insurance", {"ticket_id": ticket_id, "plan": insurance_plan})
                    show_response(resp, "Insurance Addition")

                if class_type == "business" and "priority_boarding" not in skip_steps:
                    resp = call_tool("priority_boarding", {"ticket_id": ticket_id, "class_type": class_type})
                    show_response(resp, "Priority Boarding")

                if selected_discount != "None" and "apply_discount" not in skip_steps:
                    resp = call_tool("apply_discount", {"ticket_id": ticket_id, "discount_code": selected_discount})
                    show_response(resp, "Discount Application")

                if ff_rewards and "apply_rewards" not in skip_steps:
                    resp = call_tool("apply_rewards", {"ticket_id": ticket_id, "traveler_id": traveler_name})
                    show_response(resp, "Frequent Flyer Rewards")

                if contact_cust and "contact_customer" not in skip_steps:
                    resp = call_tool("contact_customer", {"ticket_id": ticket_id})
                    show_response(resp, "Contact Customer")

                st.session_state["latest_ticket_id"] = ticket_id
                st.session_state["payment_done"] = False
                update_rules_state() # Refresh rules after booking

# --- Payment & Confirmation ---
if "latest_ticket_id" in st.session_state:
    ticket_id = st.session_state["latest_ticket_id"]
    st.markdown("## 💳 Post-Booking Actions")

    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.get("payment_done", False) and "payment" not in skip_steps:
            if st.button("💳 Pay Now"):
                res = call_tool("payment", {"ticket_id": ticket_id})
                show_response(res, "Payment")
                if res.get("status") == "payment_success":
                    st.session_state["payment_done"] = True
                    update_rules_state() # Refresh rules after payment

    with col2:
        if st.session_state.get("payment_done", False) and "confirm_ticket" not in skip_steps:
            if st.button("✅ Confirm Booking"):
                res = call_tool("confirm_ticket", {"ticket_id": ticket_id})
                show_response(res, "Booking Confirmation")
                update_rules_state() # Refresh rules after confirmation

# --- Email Form ---
if "send_email" not in skip_steps:
    st.subheader("📧 Send Confirmation Email")
    with st.form("email_form"):
        email_tid = st.text_input("Ticket ID")
        email_id = st.text_input("Email ID")
        if st.form_submit_button("Send Email"):
            resp = call_tool("send_email", {
                "to": email_id,
                "subject": f"Ticket Confirmation for {email_tid}",
                "body": f"Your ticket ID {email_tid} has been confirmed successfully!"
            })
            show_response(resp, "Send Email")
            update_rules_state() # Refresh rules after sending email

# --- Cancel Ticket ---
if "cancel_ticket" not in skip_steps:
    st.subheader("❌ Cancel Ticket")
    with st.form("cancel_form"):
        cancel_tid = st.text_input("Ticket ID (Cancel)")
        reason = st.text_input("Reason")
        if st.form_submit_button("Cancel"):
            resp = call_tool("cancel_ticket", {"ticket_id": cancel_tid, "reason": reason})
            show_response(resp, "Cancel Ticket")
            update_rules_state() # Refresh rules after cancelling

# --- Update Traveler Info ---
if "update_traveler_info" not in skip_steps:
    st.subheader("✏️ Update Traveler Info")
    with st.form("update_info_form"):
        update_tid = st.text_input("Ticket ID")
        new_name = st.text_input("New Traveler Name")
        if st.form_submit_button("Update"):
            resp = call_tool("update_info", {"ticket_id": update_tid, "new_name": new_name})
            show_response(resp, "Update Traveler Info")
            update_rules_state() # Refresh rules after updating info

# --- Refund Status ---
if "refund_status" not in skip_steps:
    st.subheader("💸 Refund Status")
    with st.form("refund_form"):
        refund_tid = st.text_input("Ticket ID")
        if st.form_submit_button("Check Refund"):
            resp = call_tool("refund_status", {"ticket_id": refund_tid})
            show_response(resp, "Refund Status")
            update_rules_state() # Refresh rules after checking refund

