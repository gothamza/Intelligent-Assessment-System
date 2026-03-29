# main.py
import os
import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval


# Import components
from pages.login import login_page
from pages.signup import signup_page
from components.main_app import *


from src.utils.loader import load_custom_css ,load_custom_js

# ─── 1) PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="Secure App", 
    page_icon="🔐", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load your CSS file
load_custom_css("src/css/chat_button.css")
load_custom_css("src/css/profile.css")
load_custom_js("src/js/copy_button.js")


BACKEND_URL = os.getenv("BACKEND_URL")

# ─── 2) SESSION‐STATE DEFAULTS ──────────────────────────────
for key, default in {
    "token": None,
    "user_info": None,
    "current_view": "home",
    "messages": [],
    "js_token_checked": False,
    "selected_subject": "Mathématiques",
    "selected_grade": "7ème année",
    "selected_course": "",
    "custom_instructions": "",
    "selected_language": "Français",
    "selected_model": "Groq/llama-3.1-8b-instant",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.session_state.chat_input_value = ""




# ─── 7) AUTHENTICATION FLOW ─────────────────────────────────
def main():
    """Main authentication flow and routing"""
    st.session_state.force_redirect = False
    # Check if we need to force a redirect to login
    if st.session_state.get("force_redirect", False):
        st.session_state.force_redirect = False
        st.switch_page("app.py")  # Will show login page on next run

    # Step 1: Check localStorage for token on initial load
    if not st.session_state.js_token_checked:
        streamlit_js_eval(
            js_expressions="localStorage.getItem('token')", 
            key="get_token_from_js"
        )
        st.session_state.js_token_checked = True
        return  # Will rerun after JS execution
    
    # Step 2: Process localStorage token if available
    js_token_result = st.session_state.get("get_token_from_js")
    if js_token_result and isinstance(js_token_result, str) and st.session_state.token is None:
        st.session_state.token = js_token_result
    
    # Step 3: Verify token and fetch user info
    if st.session_state.token and st.session_state.user_info is None and st.session_state.force_redirect is False :
        with st.spinner("🔒 Verifying session..."):
            fetch_user_info(5.0)
    
    # Step 4: Determine UI based on auth status
    if st.session_state.token and st.session_state.user_info and not st.session_state.force_redirect:
        show_main_app()
        st.session_state.delete_confirm = False

    else:
        # Show signup page if requested, otherwise show login
        if st.session_state.get("show_signup", False):
            signup_page(on_success=set_token)
            # Add back to login button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔐 Already have an account? Log in", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()
        else:
            login_page(on_success=set_token)


if __name__ == "__main__":
    main()