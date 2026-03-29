import streamlit as st
from data.moroccan_curriculum import get_subjects_for_grade, get_courses_for_grade_subject

def sidebar(on_logout):
    """
    Renders the sidebar with navigation and logout.
    """
   

    # User profile section
    
    st.sidebar.markdown('<div class="profile-circle">👤</div>', unsafe_allow_html=True)
    if st.session_state.user_info:
        user = st.session_state.user_info.get("sub", "User")
        st.sidebar.markdown(f"<div style='text-align:center;'>Logged in as <b>{user}</b></div>", unsafe_allow_html=True)
    profile_clicked = st.sidebar.button("", key="profile_pic_btn", help="View Profile", use_container_width=True)
    st.sidebar.markdown("---")

    if profile_clicked:
        st.switch_page("pages/profile.py")

    # ===========================================
    # Language Selector (at the top)
    # ===========================================
    st.sidebar.markdown("### 🌐 Langue")
    
    # Initialize selected_language if not exists
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "Français"
    
    # Available languages
    languages = ["Français", "English", "العربية"]
    
    selected_language = st.sidebar.selectbox(
        "🌐 Langue:",
        options=languages,
        index=languages.index(st.session_state.selected_language) if st.session_state.selected_language in languages else 0,
        key="language_selector_top",
        help="Sélectionnez la langue de l'interface et des réponses"
    )
    st.session_state.selected_language = selected_language
    
    # Display selected language
    language_emoji = {"Français": "🇫🇷", "English": "🇬🇧", "العربية": "🇸🇦"}.get(selected_language, "🌐")
    st.sidebar.info(f"{language_emoji} **{selected_language}**")
    
    st.sidebar.markdown("---")

    # Navigation
    nav_items = [
        {"label": "Home", "icon": "🏠", "view": "home"},
        {"label": "Upload Documents", "icon": "📤", "view": "upload"},
        {"label": "My Documents", "icon": "📄", "view": "documents"},
        {"label": "Math Tutor Chat", "icon": "💬", "view": "chat"},
        {"label": "Generate Exam", "icon": "📝", "view": "exam_generation"},
        {"label": "Take Exam", "icon": "✅", "view": "exam_taking"},
        {"label": "Models Info", "icon": "🤖", "view": "models_info"},
        {"label": "Groq Pricing", "icon": "⚡", "view": "groq_models_info"},
        {"label": "Diagrams", "icon": "🗺️", "view": "diagrams"},
    ]
      
    st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    for item in nav_items:
        btn_label = f"{item['icon']} {item['label']}"
        is_active = st.session_state.get("current_view") == item["view"]
        btn_key = f"nav_{item['view']}"
        if st.sidebar.button(
            btn_label,
            key=btn_key,
            use_container_width=True,
            help=f"Go to {item['label']}",
            type="secondary" if not is_active else "primary"
        ):
            st.session_state.current_view = item["view"]
            st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    #       # --- Sidebar Navigation ---
    # with st.sidebar:
    #     # ... (user info and logout button) ...
    #     nav_items = [
    #             {"label": "Home", "icon": "house-door", "view": "home"},
    #             {"label": "Documents", "icon": "file-earmark-text", "view": "documents"},
    #             {"label": "Prompts", "icon": "pencil-square", "view": "prompts"},
    #             {"label": "Chat with Agents", "icon": "chat-dots", "view": "chat"},
    #         ]
        # # Extract labels and icons for the option_menu
        # options = [item["label"] for item in nav_items]
        # icons = [item["icon"] for item in nav_items]
        # label_to_view_map = {item["label"]: item["view"] for item in nav_items}
        
        # current_view = st.session_state.get("current_view", "home")

        # # Find the label and index corresponding to the current view
        # expected_label = None
        # for item in nav_items:
        #     if item["view"] == current_view:
        #         expected_label = item["label"]
        #         break
        # # Set default index only if the current view is a main navigation view
        # default_index = options.index(expected_label) if expected_label else 0

        # # Create the navigation menu
        # selected_label = option_menu(
        #     menu_title=None,
        #     options=options,
        #     icons=icons,
        #     menu_icon="cast",
        #     default_index=default_index,
            
        # )

        # # Get the view corresponding to what the user just selected in the menu
        # new_view = label_to_view_map[selected_label]

        # # Only update the view if the current view is a valid nav view AND it has changed.
        # # This prevents the logic from firing when we are on a non-nav page like 'doc_detail'.
        # if expected_label and selected_label != expected_label :
        #     st.session_state.current_view = new_view
            # st.rerun()

    st.sidebar.markdown("---")
    
    # ===========================================
    # Subject and Grade Level Selectors
    # ===========================================
    st.sidebar.markdown("### 📚 Configuration du Cours")
    
    # Initialize session state for subject, grade, course, and custom instructions
    if "selected_grade" not in st.session_state:
        st.session_state.selected_grade = "7ème année"
    if "selected_subject" not in st.session_state:
        st.session_state.selected_subject = "Mathématiques"
    if "selected_course" not in st.session_state:
        st.session_state.selected_course = ""
    if "custom_instructions" not in st.session_state:
        st.session_state.custom_instructions = ""
    
    # Grade level selector (must be first to update subjects)
    grades = [
        "7ème année",
        "8ème année",
        "9ème année",
        "10ème année",
        "11ème année",
        "12ème année"
    ]
    
    selected_grade = st.sidebar.selectbox(
        "🎓 Niveau",
        options=grades,
        index=grades.index(st.session_state.selected_grade) if st.session_state.selected_grade in grades else 0,
        key="sidebar_grade_selector",
        help="Sélectionnez votre niveau d'études"
    )
    
    # Update subjects based on selected grade
    available_subjects = get_subjects_for_grade(selected_grade)
    if not available_subjects:
        available_subjects = ["Mathématiques", "Physique", "Chimie", "Sciences de la Vie et de la Terre (SVT)"]
    
    # Reset subject if current subject is not available for selected grade
    if st.session_state.selected_subject not in available_subjects:
        st.session_state.selected_subject = available_subjects[0] if available_subjects else "Mathématiques"
    
    # Subject selector (dynamic based on grade)
    selected_subject = st.sidebar.selectbox(
        "📖 Matière",
        options=available_subjects,
        index=available_subjects.index(st.session_state.selected_subject) if st.session_state.selected_subject in available_subjects else 0,
        key="sidebar_subject_selector",
        help="Sélectionnez la matière que vous souhaitez étudier"
    )
    
    # Update session state
    if selected_grade != st.session_state.selected_grade:
        st.session_state.selected_grade = selected_grade
        # Reset course when grade changes
        st.session_state.selected_course = ""
        st.rerun()
    
    if selected_subject != st.session_state.selected_subject:
        st.session_state.selected_subject = selected_subject
        # Reset course when subject changes
        st.session_state.selected_course = ""
        st.rerun()
    
    # Course selector (dynamic based on grade + subject)
    available_courses = get_courses_for_grade_subject(selected_grade, selected_subject)
    
    if available_courses:
        # Reset course if current course is not available for selected grade/subject
        if st.session_state.selected_course not in available_courses:
            st.session_state.selected_course = available_courses[0] if available_courses else ""
        
        selected_course = st.sidebar.selectbox(
            "📝 Cours/Thème",
            options=available_courses,
            index=available_courses.index(st.session_state.selected_course) if st.session_state.selected_course in available_courses else 0,
            key="sidebar_course_selector",
            help="Sélectionnez le cours ou thème spécifique à étudier"
        )
        st.session_state.selected_course = selected_course
    else:
        st.sidebar.info("ℹ️ Aucun cours disponible pour cette combinaison")
        st.session_state.selected_course = ""
    
    # Custom instructions field
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Instructions Personnalisées")
    custom_instructions = st.sidebar.text_area(
        "Instructions spécifiques:",
        value=st.session_state.custom_instructions,
        key="custom_instructions_input",
        help="Ajoutez des instructions qui seront incluses dans chaque prompt (ex: 'Utilisez des exemples concrets', 'Expliquez étape par étape', etc.)",
        height=100,
        placeholder="Ex: Expliquez toujours avec des exemples concrets de la vie quotidienne..."
    )
    st.session_state.custom_instructions = custom_instructions
    
    # Display current selection
    course_display = f" - {selected_course}" if st.session_state.selected_course else ""
    selected_language = st.session_state.get("selected_language", "Français")
    st.sidebar.info(f"📌 **Configuration actuelle:**\n{selected_subject}{course_display}\n{selected_grade}")
    
    st.sidebar.markdown("---")
    
    # ===========================================
    # Model Selector (Groq only)
    # ===========================================
    st.sidebar.markdown("### 🤖 Modèle IA")
    
    # Initialize selected_model if not exists
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "Groq/llama-3.1-8b-instant"
    
    # Liste des modèles Groq disponibles (affichage)
    groq_models_display = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile", 
        "deepseek-r1-distill-llama-70b",
        "qwen/qwen3-32b",
        "gpt-oss-20b",
        "gpt-oss-120b"
    ]
    
    # Mapping: display_name -> backend_key (sans préfixe Groq/)
    # Note: backend_key is the part after "Groq/" in AVAILABLE_MODELS
    # For qwen/qwen3-32b, the backend key is "qwen/qwen3-32b" (matches AVAILABLE_MODELS["Groq/qwen/qwen3-32b"])
    model_mapping = {
        "llama-3.1-8b-instant": "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile": "llama-3.1-70b-versatile",
        "deepseek-r1-distill-llama-70b": "deepseek-r1-distill-llama-70b",
        "qwen/qwen3-32b": "qwen/qwen3-32b",  # Backend key matches AVAILABLE_MODELS["Groq/qwen/qwen3-32b"]
        "gpt-oss-20b": "gpt-oss-20b",
        "gpt-oss-120b": "gpt-oss-120b"
    }
    
    # Icons pour chaque modèle
    model_icons = ["⚡", "🧠", "🔬", "💡", "🚀", "🌟"]
    
    # Trouver l'index du modèle actuel
    current_model = st.session_state.get("selected_model", "Groq/llama-3.1-8b-instant")
    # Extraire juste le nom du modèle (sans "Groq/")
    current_model_backend_key = current_model.replace("Groq/", "") if current_model.startswith("Groq/") else current_model
    
    # Trouver le display name correspondant
    current_model_display = None
    for display_name, backend_key in model_mapping.items():
        if backend_key == current_model_backend_key:
            current_model_display = display_name
            break
    
    if current_model_display is None:
        current_model_display = groq_models_display[0]
    
    try:
        current_index = groq_models_display.index(current_model_display) if current_model_display in groq_models_display else 0
    except ValueError:
        current_index = 0
    
    # Utiliser selectbox pour le sélecteur de modèle (plus fiable que option_menu dans sidebar)
    selected_model_display = st.sidebar.selectbox(
        "🤖 Sélectionner le modèle:",
        options=groq_models_display,
        index=current_index,
        key="model_selector",
        help="Choisissez le modèle Groq à utiliser pour le chat"
    )
    
    # Convertir le display name en backend key
    selected_model_backend_key = model_mapping.get(selected_model_display, selected_model_display)
    
    # Construire le model_name complet avec le préfixe "Groq/"
    full_model_name = f"Groq/{selected_model_backend_key}"
    st.session_state.selected_model = full_model_name
    
    # Afficher le modèle sélectionné (avec le display name)
    st.sidebar.info(f"📌 **Modèle actuel:**\n{selected_model_display}")
    
    st.sidebar.markdown("---")

    # Logout button at the bottom
    if st.sidebar.button("🔓 Logout", use_container_width=True, type="primary"):
        st.session_state.current_view = "login"
        st.session_state.force_redirect = True
        on_logout()