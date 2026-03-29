import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
import os
from requests.exceptions import Timeout






BACKEND_URL = os.getenv("BACKEND_URL")

# ─── 4) CLEAR SESSION ───────────────────────────────────────
def clear_session():
    """Clear session state and remove token from localStorage"""
    # Clear Python state
    st.session_state.token = None
    st.session_state.user_info = None
    st.session_state.current_view = "login"
    st.session_state.messages = []
    st.session_state.js_token_checked = False
    
    # Remove token from localStorage
    streamlit_js_eval(
        js_expressions="localStorage.removeItem('token');", 
        key="remove_token_script"
    )
    
    # Force immediate redirect to login
    st.session_state.force_redirect = True
    st.toast("Logging out...")



# ─── 3) TOKEN VERIFICATION ──────────────────────────────────
def fetch_user_info(timeout_sec: float = 5.0) -> bool:
    """Fetch user info from backend using token"""
    if st.session_state.token is None:
        return False

    try:
        res = requests.get(
            f"{BACKEND_URL}/users/me",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=timeout_sec
        )
        if res.status_code == 200:
            st.session_state.user_info = res.json()
            return True
        elif res.status_code == 401:
            st.error("⚠️ Session expired. Please log in again.")
            clear_session()
        else:
            st.error(f"⚠️ Backend error: {res.status_code}")
            clear_session()
    except Timeout:
        st.error(f"⏱️ Verification timed out after {timeout_sec}s.")
        clear_session()
    except requests.RequestException as e:
        st.error(f"⚠️ Network error: {str(e)}")
        clear_session()
    return False


# ─── 8) LOGIN SUCCESS HANDLER ───────────────────────────────
def set_token(token_value: str):
    """Handle successful login by setting token and persisting to localStorage"""
    st.session_state.token = token_value
    streamlit_js_eval(
        js_expressions=f"localStorage.setItem('token','{token_value}');", 
        key="set_token_eval"
    )
    st.switch_page("app.py")