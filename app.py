import streamlit as st
import hashlib
import requests
import json
from datetime import datetime

# Configure page FIRST - BEFORE any other st commands
st.set_page_config(
    page_title="Gmail Assistant",
    page_icon="📧",
    layout="centered"
)

# === AUTHENTICATION CODE ===
def check_password():
    """Returns `True` if user has correct password."""
    def password_entered():
        """Checks whether password entered is correct."""
        entered_password = st.session_state["password"]
        password_hash = hashlib.sha256(entered_password.encode()).hexdigest()
        correct_hash = "3aca9537d55cfd69afb80fb3d541799abfc17dffccb64cbbd04b6b0bad322ca1"
        
        if password_hash == correct_hash:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 Enter Password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        st.stop()

check_password()
# === END AUTHENTICATION CODE ===

# Rest of your code stays the same...


# Configure page (this must come AFTER authentication but BEFORE any other st commands)
st.set_page_config(
    page_title="Gmail Assistant",
    page_icon="📧",
    layout="centered"
)

# MCP Server URL
MCP_URL = "https://hstest-agent-tool-68934942232.us-central1.run.app/mcp"

def call_mcp_tool(tool_name, parameters):
    """Call the MCP server"""
    try:
        response = requests.post(
            MCP_URL,
            json={
                "tool": tool_name,
                "parameters": parameters
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def format_email_summary(emails):
    """Format emails for display"""
    if not emails:
        return "No emails found."
    
    summary = f"📬 Found {len(emails)} emails:\n\n"
    for idx, email in enumerate(emails, 1):
        summary += f"**{idx}. {email['subject']}**\n"
        summary += f"From: {email['from']}\n"
        summary += f"Date: {email['date']}\n"
        summary += f"Preview: {email['snippet'][:100]}...\n\n"
    return summary

# App Title
st.title("📧 Gmail Assistant")
st.markdown("Ask me about your emails!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about your emails?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process the query
    with st.chat_message("assistant"):
        with st.spinner("Checking your emails..."):
            # Determine what to do based on the query
            query_lower = prompt.lower()
            
            if "recent" in query_lower or "latest" in query_lower or "last" in query_lower:
                # Get recent emails
                days = 7
                if "today" in query_lower:
                    days = 1
                elif "week" in query_lower:
                    days = 7
                elif "month" in query_lower:
                    days = 30
                
                result = call_mcp_tool("get_recent_summary", {"days": days, "max_results": 10})
                
                if result.get("success"):
                    emails = result.get("emails", [])
                    response = format_email_summary(emails)
                else:
                    response = f"❌ Error: {result.get('error', 'Unknown error')}"
            
            elif "search" in query_lower or "find" in query_lower:
                # Extract search terms (simple approach)
                search_query = prompt.replace("search", "").replace("find", "").strip()
                
                result = call_mcp_tool("search_emails", {"query": search_query, "max_results": 10})
                
                if result.get("success"):
                    emails = result.get("emails", [])
                    response = format_email_summary(emails)
                else:
                    response = f"❌ Error: {result.get('error', 'Unknown error')}"
            
            else:
                # Default: show recent emails
                result = call_mcp_tool("get_recent_summary", {"days": 7, "max_results": 5})
                
                if result.get("success"):
                    emails = result.get("emails", [])
                    response = format_email_summary(emails)
                else:
                    response = f"❌ Error: {result.get('error', 'Unknown error')}"
            
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
with st.sidebar:
    st.header("📱 About")
    st.info("""
    This app connects to your Gmail via the MCP server.
    
    **Try asking:**
    - "Show my recent emails"
    - "What are my latest emails?"
    - "Search for emails from John"
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

