import streamlit as st




# Load external CSS
def load_custom_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    


# Load external JS
def load_custom_js(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)