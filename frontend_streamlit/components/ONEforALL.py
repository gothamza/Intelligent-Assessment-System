import streamlit as st
import streamlit.components.v1 as components
import os

def one_for_all_ui():
    """
    Loads and renders the custom HTML/JS chat interface by combining separate
    HTML, CSS, and JS files and injecting necessary backend information.
    """
    try:
        # Define paths to the component files
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        html_path = os.path.join(base_dir, 'html', 'oneforall_chat_ui.html')
        css_path = os.path.join(base_dir, 'css', 'oneforall_chat.css')
        js_path = os.path.join(base_dir, 'js', 'oneforall_chat.js')

        # Load the content of each file
        with open(html_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Get dynamic data to inject into the UI
        backend_url = os.getenv("BACKEND_URL", "")
        token = st.session_state.get('token', '')

        if not backend_url or not token:
            st.error("Application is not configured correctly. Missing Backend URL or Token.")
            return

        # 1. Inject CSS and JS into the HTML template
        final_html = html_template.replace('{{CSS_CONTENT}}', css_content)
        final_html = final_html.replace('{{JS_CONTENT}}', js_content)

        # 2. Inject dynamic data into the combined HTML
        final_html = final_html.replace('{{BACKEND_URL}}', backend_url)
        final_html = final_html.replace('{{TOKEN}}', token)

        # Render the custom chat UI in Streamlit
        st.components.v1.html(final_html, height=700, scrolling=True)
            # --- Auth & Chat List ---
    

    except FileNotFoundError as e:
        st.error(f"Error: A required UI file was not found. {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the chat UI: {e}")
