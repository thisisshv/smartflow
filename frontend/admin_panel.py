import streamlit as st
import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # Replace if deployed elsewhere

st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Smartflow Admin Panel")

# --- Command Input ---
with st.form("admin_form"):
    st.subheader("Enter a command to change the workflow")
    command = st.text_area("Command (in plain English)", height=150, placeholder="E.g., Skip the confirmation step")
    submitted = st.form_submit_button("Send")

if submitted and command:
    try:
        response = requests.post(f"{BASE_URL}/execute", params={"command": command})
        data = response.json()

        if response.status_code == 200:
            st.success("✅ Command processed successfully!")

            # Show updated rules if any
            if "new_rules" in data:
                st.subheader("🧠 Updated Business Rules")
                st.json(data["new_rules"])

            # Show raw LLM response
            if "raw_response" in data:
                st.subheader("📦 Raw LLM Response")
                st.code(data["raw_response"], language="json")
            else:
                st.warning("❌ No raw_response returned.")
        else:
            st.error("❌ Failed to process command.")
            st.json(data)

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# --- RESET Button ---
st.markdown("---")
st.subheader("Reset All Business Rules")
if st.button("🔁 Reset Rules to Default"):
    try:
        reset_payload = {
            "skip_steps": [],
            "force_steps": [],
            "tool_substitutions": {},
            "discount": {
                "enabled": False,
                "amount_percent": 0,
                "expires_at": "2025-01-01T00:00:00"
            }
        }
        res = requests.post(f"{BASE_URL}/update-rules", json=reset_payload)
        data = res.json()
        if res.status_code == 200:
            st.success("✅ All rules reset to default!")
            st.subheader("🧠 Current Rules After Reset")
            st.json(data)
        else:
            st.error("❌ Failed to reset rules.")
            st.json(data)
    except Exception as e:
        st.error(f"⚠️ Error during reset: {str(e)}")
