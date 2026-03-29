import streamlit as st
import requests
from requests.exceptions import Timeout
import os
# Use Docker-friendly default for BACKEND_URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def login_page(on_success):
    """
    Renders a login form. On success calls on_success(token).
    """
    st.markdown("## 🔐 Login")
    st.markdown("---")
    
    # Clear any residual force_redirect flag
    if "force_redirect" in st.session_state:
        del st.session_state["force_redirect"]

    # st.session_state.force_redirect = False

    # Track loading state to prevent multiple submissions
    if "login_loading" not in st.session_state:
        st.session_state.login_loading = False

    with st.form("login_form"):
        email = st.text_input("📧 Email or Username", placeholder="user@example.com or username")
        password = st.text_input("🔒 Password", type="password")
        submit = st.form_submit_button("Login", disabled=st.session_state.login_loading, use_container_width=True)
    
    # Add signup link
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📝 Don't have an account? Sign up", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()

    if submit and not st.session_state.login_loading:
        if not email or not password:
            st.warning("⚠️ Please fill in both email and password.")
            return
        st.session_state.login_loading = True
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={"username": email, "password": password},
                timeout=5
            )
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                
                if token:
                    on_success(token)
                    st.session_state.force_redirect = False
                    st.session_state.current_view = "home"
                    st.success("✅ Login successful! Redirecting...")
                else:
                    st.error("❌ Login failed: No token returned from backend.")
            elif resp.status_code == 401:
                st.error("❌ Invalid credentials. Please try again.")
            else:
                st.error(f"❌ Login failed: {resp.status_code}")
        except Timeout:
            st.error("⏰ Login request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ Login error: {e}")
        finally:
            st.session_state.login_loading = False

