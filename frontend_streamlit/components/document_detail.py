# components/document_detail.py
import streamlit as st
import requests
import os
import pandas as pd
import pypdf
from requests.exceptions import RequestException
from components.document_list import delete_document_ui
from streamlit_pdf_viewer import pdf_viewer
import webbrowser
from io import BytesIO
import docx2txt
import mammoth
from streamlit.components.v1 import html as st_html



BACKEND_URL = os.getenv("BACKEND_URL")

def document_detail():
    doc = st.session_state.get("selected_doc")
    if not doc:
        st.error("No document selected")
        st.session_state.current_view = "documents"
        st.rerun()

    st.markdown(f"## 📄 {doc['doc_title']}")
    st.markdown("---")
    st.write(f"**Type:** {doc['file_type'].upper()}")
    st.write(f"**Visibility:** {doc['visibility'].capitalize()}")
    st.write(f"**Uploaded:** {doc['upload_date']}")
    st.markdown("### Document Preview")

    user_id = doc.get("user_id")
    doc_id = doc.get("doc_id")
    filename = doc.get("doc_title")
    file_url = f"{BACKEND_URL}/files/{doc_id}"
    try:
        headers = {}
        if "access_token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
        response = requests.get(file_url, headers={"Authorization": f"Bearer {st.session_state.token}"})
        response.raise_for_status()
        file_bytes = response.content
        # Add the download button here
        st.download_button(
            label="📥 Download File",
            data=file_bytes,
            file_name=doc["doc_title"],
            mime=f"application/{doc['file_type']}",
            use_container_width=True
        )
        if doc["file_type"] == "pdf":
            
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            if 'total_pages' not in st.session_state:
                st.session_state.total_pages = 0

            try:
                pdf_reader = pypdf.PdfReader(BytesIO(file_bytes), strict=False)
                st.session_state.total_pages = len(pdf_reader.pages)
                if 'last_loaded_doc_id' not in st.session_state or st.session_state.last_loaded_doc_id != doc_id:
                    st.session_state.current_page = 1
                    st.session_state.last_loaded_doc_id = doc_id
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
                st.session_state.total_pages = 0
                st.session_state.current_page = 1

            if st.session_state.total_pages > 0:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button('Previous Page') and st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
                        st.rerun()
                with col2:
                    st.write(f"Page {st.session_state.current_page} of {st.session_state.total_pages}")
                with col3:
                    if st.button('Next Page') and st.session_state.current_page < st.session_state.total_pages:
                        st.session_state.current_page += 1
                        st.rerun()

                pdf_viewer(input=file_bytes, width=700, pages_to_render=[st.session_state.current_page] , annotations=[])

        elif doc["file_type"] == "xlsx":
            
            df = pd.read_excel(BytesIO(file_bytes))
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            st.success("✅ Excel file loaded interactively. Changes are not saved.")

        elif doc["file_type"] == "txt":
            st.code(file_bytes.decode("utf-8"), language='text')
        
        elif doc["file_type"] == "csv":
            from io import StringIO
            csv_data = StringIO(file_bytes.decode("utf-8"))
            df = pd.read_csv(csv_data)
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            st.success("✅ CSV file loaded interactively. Changes are not saved.")
        elif doc["file_type"] == "json":
            import json
            try:
                json_data = json.loads(file_bytes.decode("utf-8"))
                st.json(json_data)
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
        elif doc["file_type"] == "md":
            st.markdown(file_bytes.decode("utf-8"))
        
        elif doc["file_type"] in ["jpg", "jpeg", "png"]:
            from PIL import Image
            image = Image.open(BytesIO(file_bytes))
            st.image(image, caption=doc['doc_title'], use_column_width=True)
        elif doc["file_type"] == "docx":
            # try:
            #     text = docx2txt.process(BytesIO(file_bytes))
            #     st.text_area("Content", text, height=400)
            # except Exception as e:
            #     st.error(f"Error reading DOCX file: {e}")
            
            try:
                # Convert DOCX to HTML using mammoth
                result = mammoth.convert_to_html(BytesIO(file_bytes))
                html_content = result.value # The converted HTML
                
                # st.markdown(
                #     """
                #     <style>
                #     img {
                #         max-width: 100%;
                #         height: auto;
                #     }
                #     </style>
                #     """,
                #     unsafe_allow_html=True,
                # )
                # # Display the HTML in Streamlit
                # st.markdown(html_content, unsafe_allow_html=True)
                # --- SOLUTION FOR STYLING INSIDE AN IFRAME ---
                # Define the CSS style as a string, now including table styles
                responsive_style = """
                <style>
                body {
                    font-family: sans-serif;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
                /* --- ADD THESE STYLES FOR TABLES --- */
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 1em;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                /* ------------------------------------ */
                </style>
                """
                
                # Prepend the style to the HTML content
                full_html_with_style = responsive_style + html_content
                
                # Render the combined HTML inside the component
                st_html(full_html_with_style, height=600, scrolling=True)
                
                # st_html(html_content, height=600, scrolling=True)
                
            except Exception as e:
                st.error(f"Error rendering DOCX file: {e}")

            
      
        else:
            st.info(f"Preview not available for {doc['file_type']} files")

    except Exception as e:
        st.error(f"Could not load document: {e}")

    # Delete button with confirmation
    if "delete_confirm" not in st.session_state:
        st.session_state.delete_confirm = False

    if st.session_state.delete_confirm:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Delete", type="primary"):
                delete_document_ui(doc_id, st.session_state.token)
                st.session_state.current_view = "documents"
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.delete_confirm = False
                st.rerun()
    else:
        if st.button("🗑️ Delete Document", type="secondary"):
            st.session_state.delete_confirm = True
            st.rerun()

    if st.button("← Back to Document List"):
        st.session_state.current_view = "documents"
        st.session_state.delete_confirm = False
        st.rerun()
