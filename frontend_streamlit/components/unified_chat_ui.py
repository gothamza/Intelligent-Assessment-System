import streamlit as st
import requests
import os
from components.llm_chat import display_chat_selector
from components.chats_manager import handle_chat_delete, handle_chat_create, handle_chat_load_failure
from components.prompt_management_ui import get_prompts, display_prompt_selector

BACKEND_URL = os.getenv("BACKEND_URL")

def show_unified_chat_ui():
    st.subheader("🤖 Unified AI Assistant")
    st.markdown("---")

    # --- Auth & Chat List ---
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    resp = requests.get(f"{BACKEND_URL}/chats/list", params={"chat_type": "unified"}, headers=headers)
    if resp.status_code != 200:
        handle_chat_load_failure()
        return
    chats = resp.json()
    chat_id = display_chat_selector(chats, "unified_chat_selector")
    handle_chat_delete(chat_id, headers)
    handle_chat_create(headers, chat_type="unified")

    # --- Prompt Selector ---
    prompts = get_prompts(headers)
    selected_prompt = display_prompt_selector(prompts, key="unified_prompt_selector")
    if not chat_id:
        st.info("Select or create a chat to begin.")
        return

    # --- Cached docs list ---
    try:
        docs_resp = requests.get(f"{BACKEND_URL}/docs/list", headers=headers, timeout=10)
        all_docs = docs_resp.json() if docs_resp.status_code == 200 else []
    except:
        all_docs = []

    # --- Show Chat History ---
    msgs = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers).json().get("messages", [])
    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # --- Inline “Toolbar” Above Input ---
    col_attach, col_existing, col_scrape, _ = st.columns([1,1,1,15])
    with col_attach:
        if st.button("📎 Attach File", key="attach_btn"):
            st.session_state.show_uploader = True
    with col_existing:
        if st.button("📑 Existing Docs", key="existing_btn"):
            st.session_state.show_existing = not st.session_state.get("show_existing", False)
    with col_scrape:
        if st.button("🌐 Scrape URL", key="scrape_btn"):
            st.session_state.show_scraper = not st.session_state.get("show_scraper", False)

    # --- Conditional UIs ---
    selected_doc_ids = []

    # 1) Inline uploader
    if st.session_state.get("show_uploader"):
        files = st.file_uploader(
            "Select document(s)", type=["pdf","txt","csv"],
            accept_multiple_files=True, key="inline_uploader"
        )
        if files:
            for f in files:
                payload = {"file": (f.name, f.getvalue())}
                requests.post(f"{BACKEND_URL}/docs/upload", files=payload, headers=headers)
            st.session_state.show_uploader = False
            st.experimental_rerun()

    # 2) Existing docs picker
    if st.session_state.get("show_existing"):
        opts = {d["doc_title"]: d["doc_id"] for d in all_docs}
        pick = st.multiselect("Select from existing docs", options=list(opts.keys()), key="inline_existing")
        selected_doc_ids = [opts[p] for p in pick]

    # 3) URL scraper
    if st.session_state.get("show_scraper"):
        url = st.text_input("Enter URL to scrape", key="inline_scrape")
        if url:
            requests.post(f"{BACKEND_URL}/scrape", json={"url": url}, headers=headers)
            st.session_state.show_scraper = False
            st.experimental_rerun()

    # --- Chat Input & Send ---
    user_text = st.chat_input("Ask a question or talk to your docs…")
    if user_text:
        # Build prompt
        prompt_text = f"{selected_prompt}\n\n{user_text}" if selected_prompt else user_text

        # Save user message
        requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/add_message",
            json={"chat_id": chat_id, "role": "user", "content": prompt_text},
            headers=headers
        )
        st.chat_message("user").markdown(user_text)

        # Call unified_chat
        payload = {
            "chat_id": chat_id,
            "doc_ids": selected_doc_ids,
            "messages": [{"role": "user", "content": prompt_text}]
        }
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                r = requests.post(
                    f"{BACKEND_URL}/unified_chat",
                    json=payload,
                    headers=headers,
                    timeout=300
                )
                if r.status_code != 200:
                    st.error(f"Error: {r.status_code} – {r.text}")

        # Reset any toggles
        st.session_state.show_existing = False
        st.experimental_rerun()
