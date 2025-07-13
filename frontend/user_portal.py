import streamlit as st
import requests
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000"  # or your deployed API URL

st.set_page_config(page_title="🎟️ Book Your Flight", layout="wide")

st.title("🎟️ Smart Ticket Booking Portal")

# Sidebar Reports
with st.sidebar:
    st.header("📊 Booking Reports")
    if st.button("📝 View All Bookings"):
        res = requests.get(f"{BASE_URL}/report")
        st.json(res.json())

# Get current rules from backend
rules = requests.get(f"{BASE_URL}/rules").json()
skip_steps = set(rules.get("skip_steps", []))
force_steps = set(rules.get("force_steps", []))
substitutions = rules.get("tool_substitutions", {})
discount_config = rules.get("discount", {})

# --- Active Discount Notice ---
if discount_config.get("enabled"):
    percent = discount_config.get("amount_percent")
    expiry = discount_config.get("expires_at")
    st.markdown(f"### 🎉 {percent}% discount active until {expiry}")


def call_tool(tool_name, payload):
    actual_tool = substitutions.get(tool_name, tool_name)
    if actual_tool in skip_steps:
        return {"status": "skipped by rule"}
    try:
        return requests.post(f"{BASE_URL}/{actual_tool.replace('_', '-')}", json=payload).json()
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
            ticket_resp = call_tool("book_ticket", {
                "from_city": from_city,
                "to_city": to_city,
                "date": travel_date.isoformat(),
                "traveler_name": traveler_name
            })
            ticket_id = ticket_resp.get("ticket_id")
            st.success(f"🎫 Ticket ID: {ticket_id}")
            st.json(ticket_resp)

            if ticket_id:
                if baggage_kg > 0 and "baggage_upgrade" not in skip_steps:
                    st.json(call_tool("baggage_upgrade", {"ticket_id": ticket_id, "extra_kg": baggage_kg}))
                if seat and "select_seat" not in skip_steps:
                    st.json(call_tool("select_seat", {"ticket_id": ticket_id, "seat_number": seat}))
                if insurance_plan != "None" and "add_insurance" not in skip_steps:
                    st.json(call_tool("add_insurance", {"ticket_id": ticket_id, "plan": insurance_plan}))
                if class_type == "business" and "priority_boarding" not in skip_steps:
                    st.json(call_tool("priority_boarding", {"ticket_id": ticket_id, "class_type": class_type}))
                if selected_discount != "None" and "apply_discount" not in skip_steps:
                    st.json(call_tool("apply_discount", {"ticket_id": ticket_id, "discount_code": selected_discount}))
                if ff_rewards and "apply_rewards" not in skip_steps:
                    st.json(call_tool("apply_rewards", {"ticket_id": ticket_id, "traveler_id": traveler_name}))
                if contact_cust and "contact_customer" not in skip_steps:
                    st.json(call_tool("contact_customer", {"ticket_id": ticket_id}))

                st.session_state["latest_ticket_id"] = ticket_id
                st.session_state["payment_done"] = False

# --- Payment & Confirmation ---
if "latest_ticket_id" in st.session_state:
    ticket_id = st.session_state["latest_ticket_id"]
    st.markdown("## 💳 Post-Booking Actions")

    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.get("payment_done", False) and "process_payment" not in skip_steps:
            if st.button("💳 Pay Now"):
                res = call_tool("process_payment", {"ticket_id": ticket_id})
                st.json(res)
                st.session_state["payment_done"] = True

    with col2:
        if st.session_state.get("payment_done", False) and "confirm_booking" not in skip_steps:
            if st.button("✅ Confirm Booking"):
                res = call_tool("confirm_booking", {"ticket_id": ticket_id})
                st.json(res)

# --- Email Form ---
if "send_email" not in skip_steps:
    st.subheader("📧 Send Confirmation Email")
    with st.form("email_form"):
        email_tid = st.text_input("Ticket ID")
        email_id = st.text_input("Email ID")
        if st.form_submit_button("Send Email"):
            st.json(call_tool("send_email", {"ticket_id": email_tid, "email": email_id}))

# --- Cancel Ticket ---
if "cancel_ticket" not in skip_steps:
    st.subheader("❌ Cancel Ticket")
    with st.form("cancel_form"):
        cancel_tid = st.text_input("Ticket ID (Cancel)")
        reason = st.text_input("Reason")
        if st.form_submit_button("Cancel"):
            st.json(call_tool("cancel_ticket", {"ticket_id": cancel_tid, "reason": reason}))

# --- Update Traveler Info ---
if "update_traveler_info" not in skip_steps:
    st.subheader("✏️ Update Traveler Info")
    with st.form("update_info_form"):
        update_tid = st.text_input("Ticket ID")
        new_name = st.text_input("New Traveler Name")
        if st.form_submit_button("Update"):
            st.json(call_tool("update_traveler_info", {"ticket_id": update_tid, "new_name": new_name}))

# --- Refund Status ---
if "refund_status" not in skip_steps:
    st.subheader("💸 Refund Status")
    with st.form("refund_form"):
        refund_tid = st.text_input("Ticket ID")
        if st.form_submit_button("Check Refund"):
            st.json(call_tool("refund_status", {"ticket_id": refund_tid}))
