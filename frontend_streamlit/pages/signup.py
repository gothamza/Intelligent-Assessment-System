import streamlit as st
import requests
from requests.exceptions import Timeout
import os
# Use Docker-friendly default for BACKEND_URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def signup_page(on_success):
    """
    Renders a signup/registration form. On success calls on_success(token).
    """
    st.markdown("## 📝 Create Account")
    st.markdown("---")
    
    # Track loading state to prevent multiple submissions
    if "signup_loading" not in st.session_state:
        st.session_state.signup_loading = False

    with st.form("signup_form"):
        st.markdown("### Personal Information")
        full_name = st.text_input("👤 Full Name", placeholder="John Doe")
        
        st.markdown("### Account Details")
        email = st.text_input("📧 Email", placeholder="user@example.com")
        username = st.text_input("👤 Username", placeholder="johndoe")
        password = st.text_input("🔒 Password", type="password", help="Minimum 6 characters")
        password_confirm = st.text_input("🔒 Confirm Password", type="password")
        
        submit = st.form_submit_button("Create Account", disabled=st.session_state.signup_loading, use_container_width=True)

    if submit and not st.session_state.signup_loading:
        # Validation
        if not email or not username or not password:
            st.warning("⚠️ Please fill in all required fields.")
            return
        
        if len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters long.")
            return
        
        if password != password_confirm:
            st.warning("⚠️ Passwords do not match.")
            return
        
        # Basic email validation
        if "@" not in email or "." not in email:
            st.warning("⚠️ Please enter a valid email address.")
            return
        
        st.session_state.signup_loading = True
        
        try:
            # Register user
            resp = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "email": email,
                    "username": username,
                    "password": password,
                    "full_name": full_name if full_name else None
                },
                timeout=10
            )
            
            if resp.status_code == 200:
                st.success("✅ Account created successfully! Logging you in...")
                
                # Automatically log in the user after successful registration
                # Use email as login (backend uses email as login field)
                login_identifier = email if email else username
                try:
                    login_resp = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        data={"username": login_identifier, "password": password},
                        timeout=5
                    )
                    
                    if login_resp.status_code == 200:
                        token = login_resp.json().get("access_token")
                        if token:
                            on_success(token)
                            st.session_state.force_redirect = False
                            st.session_state.current_view = "home"
                            st.rerun()
                        else:
                            st.error("❌ Registration successful but login failed. Please try logging in manually.")
                    else:
                        st.warning("⚠️ Account created but auto-login failed. Please log in manually.")
                except Exception as e:
                    st.warning(f"⚠️ Account created but auto-login failed: {str(e)}. Please log in manually.")
                    
            elif resp.status_code == 400:
                error_detail = resp.json().get("detail", "Registration failed")
                if "already registered" in error_detail.lower():
                    st.error("❌ This email is already registered. Please use a different email or try logging in.")
                elif "already taken" in error_detail.lower():
                    st.error("❌ This username is already taken. Please choose a different username.")
                else:
                    st.error(f"❌ {error_detail}")
            else:
                error_detail = resp.json().get("detail", "Registration failed")
                st.error(f"❌ Registration failed: {error_detail}")
                
        except Timeout:
            st.error("⏰ Registration request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to server. Please check if the backend is running.")
        except Exception as e:
            st.error(f"❌ Registration error: {str(e)}")
        finally:
            st.session_state.signup_loading = False

