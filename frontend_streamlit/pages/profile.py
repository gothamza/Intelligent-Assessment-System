import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def show_profile():
    st.title("👤 Profile")
    token = st.session_state.get("token")
    if not token:
        st.warning("You must be logged in to view your profile.")
        st.stop()

    # Try to get user info from session or backend
    user_info = st.session_state.get("user_info")
    if not user_info:
        try:
            resp = requests.get(
                f"{BACKEND_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            if resp.status_code == 200:
                user_info = resp.json()
                st.session_state["user_info"] = user_info
            else:
                st.error("Failed to fetch user info.")
                st.stop()
        except Exception as e:
            st.error(f"Error fetching user info: {e}")
            st.stop()
    user = st.session_state.user_info.get("sub", "User")
    st.subheader("User Information")
    st.write(f"**Name:** {user_info.get('full_name', 'N/A')}")
    st.write(f"**Email:** {user}")
    st.write(f"**User ID:** {user_info.get('id', 'N/A')}")
    st.write(f"**Role:** {user_info.get('role', 'N/A')}")
    st.write(f"**Joined:** {user_info.get('created_at', 'N/A')}")

    # Optionally, add more fields or allow editing profile
show_profile()