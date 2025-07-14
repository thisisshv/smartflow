import streamlit as st
import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # Replace if deployed elsewhere

st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Smartflow Admin Panel")

def show_response(resp, action_desc="Action"):
    if not resp:
        st.error("❌ No response received.")
        return
    status = resp.get("status", "")
    if status in ["success", "updated", "changed", "executed"]:
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

# --- Command Input ---
with st.form("admin_form"):
    st.subheader("Enter a command to change the workflow")
    command = st.text_area("Command (in plain English)", height=150, placeholder="E.g., Skip the confirmation step")
    submitted = st.form_submit_button("Send")

if submitted and command:
    response = requests.post(f"{BASE_URL}/execute", params={"command": command})
    try:
        data = response.json()
    except ValueError:
        st.error("❌ Backend did not return valid JSON. Raw response:")
        st.code(response.text)
        data = {}
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        data = {}

    if response.status_code == 200:
        st.success("✅ Command processed successfully!")

        # Show updated rules if any
        new_rules = data.get("new_rules")
        raw_response = data.get("raw_response")

        if new_rules:
            st.subheader("🧠 Updated Business Rules")
            st.json(new_rules)
        else:
            st.warning("⚠️ No rules were updated.")

        if raw_response:
            st.subheader("�� Raw LLM Response")
            st.code(raw_response, language="json")
        else:
            st.warning("⚠️ No raw_response received.")

    else:
        st.error("❌ Failed to process command.")
        st.json(data)

# --- RESET Button ---
st.markdown("---")
st.subheader("Reset All Business Rules")
if st.button("🔁 Reset Rules to Default"):
    try:
        res = requests.post(f"{BASE_URL}/rules/reset")
        try:
            data = res.json()
        except ValueError:
            st.error("❌ Backend did not return valid JSON. Raw response:")
            st.code(res.text)
            data = {}
        if res.status_code == 200:
            st.success("✅ All rules reset to default!")
            st.subheader("🧠 Current Rules After Reset")
            st.json(data)
        else:
            st.error("❌ Failed to reset rules.")
            st.json(data)
    except Exception as e:
        st.error(f"⚠️ Error during reset: {str(e)}")
