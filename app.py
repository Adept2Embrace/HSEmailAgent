import streamlit as st
import hashlib
import requests
import json
from datetime import datetime

# === ADD THIS AUTHENTICATION CODE ===
def check_password():
    """Returns `True` if user has correct password."""
    def password_entered():
        """Checks whether password entered is correct."""
        entered_password = st.session_state["password"]
        # Hash the password for security
        password_hash = hashlib.sha256(entered_password.encode()).hexdigest()
        # Change this hash to your password's hash
        correct_hash = "5c84822c7715c0be10ec93579c881b4f8f0e02c89c23f6a820d913adb1e80e19"
        
        if password_hash == correct_hash:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # First run, show password input
    if "password_correct" not in st.session_state:
        st.text_input("🔐 Enter Password", type="password", on_change=password_entered, key="password")
        st.stop()
    # Password incorrect, show input + error
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        st.stop()

check_password()
# === END AUTHENTICATION CODE ===

# Configure page (this should come AFTER authentication)
st.set_page_config(
    page_title="Gmail Assistant",
    page_icon="📧",
    layout="centered"
)

# Rest of your code...

