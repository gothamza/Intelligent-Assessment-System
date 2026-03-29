"""
Shared form components for the application.
"""
import streamlit as st
from typing import List, Dict, Any, Optional, Callable


def exam_creation_form() -> Dict[str, Any]:
    """Form for creating new exams"""
    st.subheader("🎯 Paramétrage et Génération")
    # Single-column layout
    # Grade selection
    grades = {
        "7e": "7ème année",
        "8e": "8ème année", 
        "9e": "9ème année",
        "10e": "10ème année",
        "11e": "11ème année",
        "12e": "12ème année"
    }
    selected_grade = st.selectbox("Niveau", list(grades.keys()), format_func=lambda x: grades[x], key="exam_grade_select")

    # Course selection
    course_options = {
        "7e": ["Nombres entiers", "Fractions", "Géométrie de base", "Proportions"],
        "8e": ["Algèbre de base", "Équations", "Géométrie", "Statistiques"],
        "9e": ["Calcul littéral", "Systèmes d'équations", "Fonctions", "Probabilités"],
        "10e": ["Fonctions quadratiques", "Trigonométrie", "Logarithmes", "Suites"],
        "11e": ["Limites", "Dérivées", "Intégrales", "Nombres complexes"],
        "12e": ["Intégrales", "Équations différentielles", "Séries", "Analyse vectorielle"]
    }

    available_courses = course_options.get(selected_grade, ["Mathématiques"])
    selected_courses = st.multiselect("Cours", available_courses, default=available_courses[:2], key="exam_courses_select")

    # Custom course input - compact controls remain inline
    with st.expander("➕ Cours personnalisés", expanded=False):
        # Initialize session state for custom courses
        if 'custom_courses_list' not in st.session_state:
            st.session_state.custom_courses_list = []

        # Compact input row
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            new_custom_course = st.text_input("Nouveau cours", placeholder="Ex: Calcul différentiel", key="new_custom_course", label_visibility="collapsed")
        with c2:
            if st.button("➕", key="add_custom_course", help="Ajouter"):
                if new_custom_course and new_custom_course not in selected_courses and new_custom_course not in st.session_state.custom_courses_list:
                    st.session_state.custom_courses_list.append(new_custom_course)
                    st.rerun()
        with c3:
            if st.button("🗑️", key="clear_all_custom_courses", help="Tout effacer"):
                st.session_state.custom_courses_list = []
                st.rerun()

        # Display as compact tags
        if st.session_state.custom_courses_list:
            tags_html = ""
            for i, custom_course in enumerate(st.session_state.custom_courses_list):
                tags_html += f'<span style="background-color: #ff6b6b; color: white; padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 12px;">{custom_course} <a href="#" onclick="removeCustomCourse({i})" style="color: white; text-decoration: none; margin-left: 4px;">×</a></span>'
            st.markdown(f'<div style="margin-top: 8px;">{tags_html}</div>', unsafe_allow_html=True)

            # Individual removal buttons (hidden but functional)
            for i, custom_course in enumerate(st.session_state.custom_courses_list):
                if st.button("", key=f"remove_custom_course_{i}", help="Supprimer", type="secondary"):
                    st.session_state.custom_courses_list.pop(i)
                    st.rerun()

        # Add custom courses to the main courses list
        if st.session_state.custom_courses_list:
            for custom_course in st.session_state.custom_courses_list:
                if custom_course not in selected_courses:
                    selected_courses.append(custom_course)

    # Subject percentage distribution
    if len(selected_courses) > 1:
        st.markdown("**Répartition des questions par cours:**")
        
        # Toggle between auto and manual mode
        col_mode1, col_mode2 = st.columns(2)
        with col_mode1:
            mode = st.radio(
                "Mode de répartition",
                ["🎯 Automatique (égale)", "✏️ Manuelle (personnalisée)"],
                key="exam_percentage_mode",
                horizontal=True
            )
        
        with col_mode2:
            if mode == "✏️ Manuelle (personnalisée)":
                auto_normalize = st.checkbox(
                    "Auto-normaliser à 100%",
                    value=True,
                    help="Ajuste automatiquement les pourcentages pour totaliser 100%",
                    key="exam_auto_normalize"
                )
            else:
                auto_normalize = False
        
        course_percentages = {}
        
        if mode == "🎯 Automatique (égale)":
            # Equal distribution
            equal_percentage = 100 // len(selected_courses)
            remainder = 100 % len(selected_courses)
            
            for i, course in enumerate(selected_courses):
                # Distribute remainder to first courses
                percentage = equal_percentage + (1 if i < remainder else 0)
                course_percentages[course] = percentage
            
            # Display as read-only info
            st.info("📊 **Répartition automatique:**")
            cols = st.columns(len(selected_courses))
            for i, (course, pct) in enumerate(course_percentages.items()):
                with cols[i]:
                    st.metric(course, f"{pct}%")
        
        else:  # Manual mode
            # Initialize session state for manual percentages
            if 'manual_percentages' not in st.session_state:
                st.session_state.manual_percentages = {}
                # Set equal distribution as default
                equal_pct = 100 // len(selected_courses)
                for i, course in enumerate(selected_courses):
                    st.session_state.manual_percentages[course] = equal_pct + (1 if i < len(selected_courses) - 1 and i < (100 % len(selected_courses)) else 0)
            
            # Update session state if courses changed
            for course in selected_courses:
                if course not in st.session_state.manual_percentages:
                    # New course - redistribute
                    equal_pct = 100 // len(selected_courses)
                    st.session_state.manual_percentages[course] = equal_pct
            
            # Remove courses that are no longer selected
            courses_to_remove = [c for c in st.session_state.manual_percentages.keys() if c not in selected_courses]
            for course in courses_to_remove:
                del st.session_state.manual_percentages[course]
            
            # Input methods toggle
            input_method = st.radio(
                "Méthode de saisie",
                ["🎚️ Sliders", "⌨️ Chiffres exacts"],
                key="exam_input_method",
                horizontal=True
            )
            
            total_percentage = 0
            
            for course in selected_courses:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if input_method == "🎚️ Sliders":
                        percentage = st.slider(
                            f"{course}",
                            min_value=0,
                            max_value=100,
                            value=st.session_state.manual_percentages.get(course, 25),
                            step=5,
                            key=f"exam_percentage_slider_{course}"
                        )
                    else:  # Number input
                        percentage = st.number_input(
                            f"{course}",
                            min_value=0,
                            max_value=100,
                            value=st.session_state.manual_percentages.get(course, 25),
                            step=1,
                            key=f"exam_percentage_number_{course}"
                        )
                
                with col2:
                    st.metric("", f"{percentage}%")
                
                course_percentages[course] = percentage
                st.session_state.manual_percentages[course] = percentage
                total_percentage += percentage
            
            # Display total and auto-normalize if enabled
            if total_percentage != 100:
                if auto_normalize:
                    # Normalize to 100%
                    if total_percentage > 0:
                        normalized_percentages = {}
                        for course, pct in course_percentages.items():
                            normalized_percentages[course] = round((pct / total_percentage) * 100)
                        
                        # Adjust for rounding errors
                        normalized_total = sum(normalized_percentages.values())
                        if normalized_total != 100:
                            # Add/subtract difference to largest percentage
                            largest_course = max(normalized_percentages, key=normalized_percentages.get)
                            normalized_percentages[largest_course] += (100 - normalized_total)
                        
                        course_percentages = normalized_percentages
                        
                        st.success(f"✅ Auto-normalisé: {total_percentage}% → 100%")
                        
                        # Show normalized distribution
                        cols = st.columns(len(selected_courses))
                        for i, (course, pct) in enumerate(course_percentages.items()):
                            with cols[i]:
                                st.caption(f"**{course}**: {pct}%")
                    else:
                        st.error("❌ Total = 0%. Impossible de normaliser.")
                else:
                    # Show warning
                    if total_percentage < 100:
                        st.warning(f"⚠️ Total: {total_percentage}% (< 100%)")
                    else:
                        st.error(f"❌ Total: {total_percentage}% (> 100%)")
            else:
                st.success(f"✅ Total: {total_percentage}% - Parfait!")
    else:
        course_percentages = {selected_courses[0]: 100} if selected_courses else {}

    # Difficulty
    difficulty = st.selectbox("Difficulté", ["Facile", "Intermédiaire", "Difficile"], key="exam_difficulty_select")

    # Number of questions
    num_questions = st.slider("Nombre de questions", 1, 20, 5)

    # Include answers
    include_answers = st.checkbox("Générer les réponses", value=True, key="creation_include_answers")
    return {
        "grade": selected_grade,
        "courses": selected_courses,
        "course_percentages": course_percentages,
        "difficulty": difficulty,
        "num_questions": num_questions,
        "include_answers": include_answers
    }


def exam_import_form() -> Dict[str, Any]:
    """Form for importing existing exams"""
    st.subheader("📥 Importer et Générer des Réponses")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choisir un fichier d'examen",
        type=['pdf', 'docx', 'txt'],
        help="Formats supportés: PDF, Word (.docx), Texte (.txt)"
    )
    
    if uploaded_file:
        st.success(f"✅ Fichier chargé: {uploaded_file.name}")
        
        # Processing options
        col1, col2 = st.columns(2)
        
        with col1:
            use_llm_extraction = st.checkbox("Utiliser l'IA pour l'extraction", value=True, key="import_llm_extraction")
            generate_answers = st.checkbox("Générer les réponses", value=True, key="import_generate_answers")
        
        with col2:
            max_tokens_question = st.number_input("Tokens max pour questions", 100, 2000, 500, key="import_tokens_question")
            max_tokens_answer = st.number_input("Tokens max pour réponses", 500, 8000, 4000, key="import_tokens_answer")
        
        return {
            "file": uploaded_file,
            "use_llm_extraction": use_llm_extraction,
            "generate_answers": generate_answers,
            "max_tokens_question": max_tokens_question,
            "max_tokens_answer": max_tokens_answer
        }
    
    return {}


def exam_editing_form(exam_data: Dict[str, Any]) -> Dict[str, Any]:
    """Form for editing exam questions"""
    st.subheader("✏️ Modifier l'Examen")
    
    # Exam title
    title = st.text_input("Titre de l'examen", value=exam_data.get("title", ""))
    
    # Questions editing
    questions = exam_data.get("questions", [])
    edited_questions = []
    
    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                question_text = st.text_area(
                    "Question",
                    value=question.get("question", ""),
                    height=100,
                    key=f"edit_q_{i}"
                )
                
                if question.get("answer"):
                    answer_text = st.text_area(
                        "Réponse",
                        value=question.get("answer", ""),
                        height=100,
                        key=f"edit_a_{i}"
                    )
                else:
                    answer_text = ""
            
            with col2:
                course = st.text_input("Cours", value=question.get("course", ""), key=f"edit_c_{i}")
                # Map difficulty values to ensure compatibility
                difficulty_mapping = {
                    "Facile": "Facile",
                    "Intermédiaire": "Intermédiaire", 
                    "Difficile": "Difficile",
                    "Moyen": "Intermédiaire",  # Map "Moyen" to "Intermédiaire"
                    "Easy": "Facile",
                    "Medium": "Intermédiaire",
                    "Hard": "Difficile"
                }
                
                current_difficulty = question.get("difficulty", "Intermédiaire")
                mapped_difficulty = difficulty_mapping.get(current_difficulty, "Intermédiaire")
                
                difficulty = st.selectbox(
                    "Difficulté",
                    ["Facile", "Intermédiaire", "Difficile"],
                    index=["Facile", "Intermédiaire", "Difficile"].index(mapped_difficulty),
                    key=f"edit_d_{i}"
                )
            
            edited_questions.append({
                "question": question_text,
                "answer": answer_text,
                "course": course,
                "difficulty": difficulty
            })
    
    return {
        "title": title,
        "questions": edited_questions
    }


def user_login_form() -> Dict[str, str]:
    """Form for user login"""
    st.subheader("🔐 Connexion")
    
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        login_clicked = st.button("Se connecter", type="primary")
    
    with col2:
        register_clicked = st.button("S'inscrire")
    
    return {
        "username": username,
        "password": password,
        "login_clicked": login_clicked,
        "register_clicked": register_clicked
    }


def user_registration_form() -> Dict[str, Any]:
    """Form for user registration"""
    st.subheader("📝 Inscription")
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input("Nom d'utilisateur")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
    
    with col2:
        confirm_password = st.text_input("Confirmer le mot de passe", type="password")
        role = st.selectbox(
            "Rôle",
            ["teacher", "student", "admin"],
            format_func=lambda x: {
                "teacher": "👨‍🏫 Enseignant",
                "student": "🎓 Étudiant", 
                "admin": "👑 Administrateur"
            }[x],
            key="auth_role_select"
        )
        
        # Additional fields for teachers
        if role == "teacher":
            grade = st.selectbox("Niveau enseigné", ["7e", "8e", "9e", "10e", "11e", "12e"], key="auth_grade_select")
            school = st.text_input("École")
        else:
            grade = None
            school = None
    
    register_clicked = st.button("S'inscrire", type="primary")
    
    return {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": confirm_password,
        "role": role,
        "grade": grade,
        "school": school,
        "register_clicked": register_clicked
    }


def exam_selection_form(exams: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Form for selecting an exam to take"""
    if not exams:
        st.info("Aucun examen disponible")
        return None
    
    st.subheader("📋 Sélectionner un Examen")
    
    exam_options = {f"{exam['title']} ({exam.get('grade', 'N/A')})": exam for exam in exams}
    selected_exam_title = st.selectbox("Choisir un examen", list(exam_options.keys()), key="exam_selection_select")
    
    if selected_exam_title:
        selected_exam = exam_options[selected_exam_title]
        
        # Display exam info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Questions", len(selected_exam.get("questions", [])))
        
        with col2:
            st.metric("Durée", f"{selected_exam.get('duration', 'N/A')} min")
        
        with col3:
            st.metric("Difficulté", selected_exam.get("difficulty", "N/A"))
        
        start_exam = st.button("Commencer l'examen", type="primary")
        
        return {
            "exam": selected_exam,
            "start_exam": start_exam
        }
    
    return None
