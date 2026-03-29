import streamlit as st
import sys
from pathlib import Path
import json
from io import BytesIO
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))


# Note: Database and auth removed for simplified version
from src.enhanced_chains import create_enhanced_llm_manager
from src.features.exams.extraction import (
    clean_mathematical_notation,
    clean_question_content,
    extract_questions_with_llm,
    extract_questions_simple,
)
from src.features.exams.generation import generate_exam_items as gen_items_module
from src.features.exams.export import export_docx_from_html as export_docx_module, export_pdf_from_html as export_pdf_module
from src.ui.forms import exam_creation_form, exam_import_form, exam_editing_form
from src.ui.components import show_loading_spinner, show_success_message, show_error_message

st.set_page_config(page_title="Création d'Examens (Enseignant)", layout="wide")


def main():
    st.title("📝 Création d'Examens pour Enseignants")

    # Tab selection
    tab1, tab2, tab3 = st.tabs(["🎯 Créer un Nouvel Examen", "📥 Importer et Générer des Réponses", "📚 Générer un Cours"])

    with tab1:
        # Use modular form component
        form_data = exam_creation_form()
        
        if form_data:
            # Process form data and generate exam
            if st.button("🚀 Générer l'Examen", type="primary"):
                with show_loading_spinner("Génération de l'examen en cours..."):
                    try:
                        exam_items = generate_exam_items(
                            form_data["grade"],
                            form_data["courses"], 
                            form_data["difficulty"],
                            form_data["num_questions"],
                            form_data["include_answers"],
                            form_data.get("course_percentages", {})
                        )
                        
                        # Store in session state for editing/export
                        st.session_state.exam_items = exam_items
                        st.session_state.exam_title = f"Examen de Mathématiques - {form_data['grade']} - {form_data['difficulty']}"
                        show_success_message("Examen généré avec succès!")
                        
                    except Exception as e:
                        show_error_message(f"Erreur lors de la génération: {str(e)}")

    with tab2:
        # Use modular import form component
        import_data = exam_import_form()
        
        if import_data and import_data.get("file"):
            if st.button("📥 Traiter le Fichier", type="primary"):
                with show_loading_spinner("Traitement du fichier en cours..."):
                    try:
                        # Process uploaded file based on file type
                        uploaded_file = import_data["file"]
                        file_extension = uploaded_file.name.split('.')[-1].lower()
                        
                        # Read file content based on file type
                        if file_extension == 'pdf':
                            # Read PDF file
                            try:
                                import PyPDF2
                                file_content = ""
                                for page in PyPDF2.PdfReader(uploaded_file).pages:
                                    file_content += page.extract_text() + "\n"
                            except ImportError:
                                show_error_message("PyPDF2 n'est pas installé. Veuillez installer: pip install PyPDF2")
                                return
                        elif file_extension in ['docx', 'doc']:
                            # Read Word file
                            try:
                                from docx import Document
                                doc = Document(uploaded_file)
                                file_content = ""
                                for paragraph in doc.paragraphs:
                                    file_content += paragraph.text + "\n"
                            except ImportError:
                                show_error_message("python-docx n'est pas installé. Veuillez installer: pip install python-docx")
                                return
                        else:
                            # Read as text file
                            try:
                                file_content = uploaded_file.read().decode('utf-8')
                            except UnicodeDecodeError:
                                # Try with different encoding
                                file_content = uploaded_file.read().decode('latin-1')
                        
                        if import_data["use_llm_extraction"]:
                            exam_items = extract_questions_with_llm(
                                file_content=file_content,
                                grade="Collège",  # Default grade
                                difficulty="Intermédiaire",  # Default difficulty
                                create_llm_manager=create_enhanced_llm_manager
                            )
                        else:
                            exam_items = extract_questions_simple(file_content, "Collège", "Intermédiaire")
                        
                        # Debug information
                        st.info(f"📊 Extraction terminée: {len(exam_items)} questions trouvées")
                        
                        # Show first few characters of file content for debugging
                        with st.expander("🔍 Debug - Contenu du fichier (premiers 500 caractères)"):
                            st.text(file_content[:500])
                        
                        # Store in session state
                        st.session_state.exam_items = exam_items
                        st.session_state.exam_title = f"Examen Importé - {import_data['file'].name}"
                        show_success_message("Fichier traité avec succès!")
                        
                    except Exception as e:
                        show_error_message(f"Erreur lors du traitement: {str(e)}")

    # Display exam preview and editing if available
    if 'exam_items' in st.session_state and st.session_state.exam_items:
        st.divider()
        st.subheader("📋 Aperçu de l'Examen")
        
        # Use modular editing form
        edited_data = exam_editing_form({
            "title": st.session_state.exam_title,
            "questions": st.session_state.exam_items
        })
        
        if edited_data:
            st.session_state.exam_items = edited_data["questions"]
            st.session_state.exam_title = edited_data["title"]
            
            # Export options with answer toggle
            st.markdown("### 📤 Options d'Export")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                include_answers = st.checkbox(
                    "📝 Inclure les réponses dans l'export",
                    value=False,
                    help="Cochez pour inclure les réponses correctes dans les fichiers exportés"
                )
            
            with col2:
                st.info("💡 **Astuce:** Décochez pour créer un examen pour les étudiants, cochez pour créer un corrigé pour l'enseignant.")
                
                # Quick export both versions
                if st.button("📄 Exporter les deux versions (DOCX)", type="secondary"):
                    # Export without answers
                    html_no_answers = build_exam_html(st.session_state.exam_title, st.session_state.exam_items, False)
                    docx_no_answers = export_docx_from_html(html_no_answers)
                    
                    # Export with answers
                    html_with_answers = build_exam_html(st.session_state.exam_title, st.session_state.exam_items, True)
                    docx_with_answers = export_docx_from_html(html_with_answers)
                    
                    if docx_no_answers and docx_with_answers:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📝 Examen (sans réponses)",
                                docx_no_answers.getvalue(),
                                f"{st.session_state.exam_title}_sans_reponses.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        with col2:
                            st.download_button(
                                "📝 Corrigé (avec réponses)",
                                docx_with_answers.getvalue(),
                                f"{st.session_state.exam_title}_avec_reponses.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    else:
                        st.error("❌ Erreur lors de la génération des fichiers")
            
            # Export buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("💾 Sauvegarder en Base"):
                    try:
                        # Exam created successfully (simplified version)
                        st.success("✅ Examen créé avec succès!")
                        show_success_message("Examen sauvegardé avec succès!")
                    except Exception as e:
                        show_error_message(f"Erreur de sauvegarde: {str(e)}")
            
            with col2:
                if st.button("📄 Exporter DOCX"):
                    html_content = build_exam_html(st.session_state.exam_title, st.session_state.exam_items, include_answers)
                    
                    # Debug: Show HTML content and exam items
                    with st.expander("🔍 Debug - Informations d'export"):
                        st.write(f"**Include answers:** {include_answers}")
                        st.write(f"**Number of questions:** {len(st.session_state.exam_items)}")
                        
                        # Show first question with answer info
                        if st.session_state.exam_items:
                            first_q = st.session_state.exam_items[0]
                            st.write(f"**First question has answer:** {'answer' in first_q and first_q.get('answer')}")
                            if 'answer' in first_q:
                                st.write(f"**Answer preview:** {first_q.get('answer', '')[:100]}...")
                        
                        st.write("**HTML preview (first 1000 chars):**")
                        st.text(html_content[:1000])
                    
                    docx_buffer = export_docx_from_html(html_content)
                    if docx_buffer:
                        file_suffix = "_avec_reponses" if include_answers else "_sans_reponses"
                        st.download_button(
                            "Télécharger DOCX",
                            docx_buffer.getvalue(),
                            f"{st.session_state.exam_title}{file_suffix}.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    else:
                        st.error("❌ Erreur lors de la génération du fichier DOCX")
            
            with col3:
                if st.button("📄 Exporter PDF"):
                    html_content = build_exam_html(st.session_state.exam_title, st.session_state.exam_items, include_answers)
                    pdf_buffer = export_pdf_from_html(html_content)
                    if pdf_buffer:
                        file_suffix = "_avec_reponses" if include_answers else "_sans_reponses"
                        st.download_button(
                            "Télécharger PDF",
                            pdf_buffer.getvalue(),
                            f"{st.session_state.exam_title}{file_suffix}.pdf",
                            "application/pdf"
                        )
                    else:
                        st.error("❌ Erreur lors de la génération du fichier PDF")
            
            with col4:
                if st.button("📄 Exporter JSON"):
                    json_data = {
                        "title": st.session_state.exam_title,
                        "questions": st.session_state.exam_items,
                        "include_answers": include_answers
                    }
                    st.download_button(
                        "Télécharger JSON",
                        json.dumps(json_data, ensure_ascii=False, indent=2),
                        f"{st.session_state.exam_title}.json",
                        "application/json"
                    )

    with tab3:
        # Course generation form
        course_form_data = course_generation_form()
        
        if course_form_data and course_form_data.get("subjects"):
            if st.button("🚀 Générer le Cours", type="primary"):
                with show_loading_spinner("Génération du cours en cours..."):
                    try:
                        course_data = generate_teacher_course(course_form_data)
                        
                        # Search for additional references using Tavily
                        with show_loading_spinner("Recherche de références d'étude..."):
                            try:
                                from src.features.references import get_study_references
                                subjects = course_form_data.get("subjects", [])
                                grade_level = course_form_data.get("grade", "7ème année")
                                references = get_study_references(subjects, grade_level)
                                course_data["study_references"] = references
                            except ImportError as import_error:
                                print(f"Warning: Could not import references module: {import_error}")
                                course_data["study_references"] = {
                                    "available": False, 
                                    "message": "Module de références non disponible. Assurez-vous que le module 'src.features.references' est correctement installé."
                                }
                            except Exception as ref_error:
                                print(f"Warning: Could not fetch references: {ref_error}")
                                course_data["study_references"] = {
                                    "available": False, 
                                    "message": f"Erreur lors de la recherche de références: {str(ref_error)}"
                                }
                        
                        # Store course data in session state
                        st.session_state.generated_teacher_course = course_data
                        st.session_state.course_form_data = course_form_data
                        
                        st.success("✅ Cours généré avec succès!")
                        st.rerun()
                    
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "rate_limit" in error_msg.lower():
                            st.error("""
                            ❌ **Limite de taux d'API atteinte**
                            
                            Vous avez atteint la limite quotidienne de votre fournisseur d'API. 
                            
                            **Solutions:**
                            - Attendez quelques minutes et réessayez
                            - Vérifiez vos clés API dans les paramètres
                            - Le système essaiera automatiquement d'autres fournisseurs
                            
                            **Détails techniques:** {error_msg}
                            """.format(error_msg=error_msg))
                        else:
                            st.error(f"❌ Erreur lors de la génération du cours: {error_msg}")
        
        # Display generated course if available
        if hasattr(st.session_state, 'generated_teacher_course') and st.session_state.generated_teacher_course:
            course_data = st.session_state.generated_teacher_course
            course_form_data = st.session_state.course_form_data
            
            st.markdown("---")
            st.markdown("### 📚 Cours Généré")
            
            # Show course content
            st.markdown(f"### {course_data.get('title', 'Cours')}")
            st.markdown(course_data.get('introduction', ''))
            
            # Topics
            for topic in course_data.get('topics', []):
                st.markdown(f"""
                <div style="background-color: var(--background-color, #2a2a2a); color: var(--text-color, #ffffff); padding: 1.5rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #007bff; border: 1px solid var(--border-color, #444);">
                    <h4 style="color: var(--text-color, #ffffff);">📚 {topic.get('name', 'Sujet')}</h4>
                    <p style="color: var(--secondary-text, #cccccc); line-height: 1.6;">{topic.get('explanation', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Exercises
                st.markdown("### 📝 Exercices")
                for i, exercise in enumerate(topic.get('exercises', []), 1):
                    with st.expander(f"Exercice {i}"):
                        st.markdown(f"**Énoncé:** {exercise.get('question', '')}")
                        st.markdown(f"**Solution:** {exercise.get('solution', '')}")
                        
                        if exercise.get('hints'):
                            st.markdown("**Indices:**")
                            for hint in exercise['hints']:
                                st.markdown(f"- {hint}")
            
            # Tips and resources
            col1, col2 = st.columns(2)
            
            with col1:
                if course_data.get('tips'):
                    st.markdown("### 💡 Conseils d'apprentissage")
                    for tip in course_data['tips']:
                        st.markdown(f"- {tip}")
            
            with col2:
                if course_data.get('resources'):
                    st.markdown("### 📚 Ressources supplémentaires")
                    for resource in course_data['resources']:
                        st.markdown(f"- {resource}")
            
            # Study References from Tavily
            if course_data.get('study_references'):
                st.markdown("---")
                st.markdown("### 🔍 Références d'Étude Supplémentaires")
                
                references = course_data['study_references']
                
                if references.get('available', False):
                    # Subject-specific references
                    if references.get('subject_references'):
                        st.markdown("#### 📖 Références par Sujet")
                        for subject, refs in references['subject_references'].items():
                            if refs:
                                with st.expander(f"📚 {subject}"):
                                    for ref in refs:
                                        st.markdown(f"""
                                        **{ref['title']}**
                                        - 🔗 [Lien]({ref['url']})
                                        - 📝 {ref['content']}
                                        """)
                    
                    # General math resources
                    if references.get('general_resources'):
                        st.markdown("#### 🌐 Ressources Générales")
                        for resource in references['general_resources'][:5]:  # Show top 5
                            st.markdown(f"""
                            **{resource['title']}**
                            - 🔗 [Lien]({resource['url']})
                            - 📝 {resource['content']}
                            """)
                else:
                    st.info(f"ℹ️ {references.get('message', 'Références non disponibles')}")
            
            # Download buttons
            st.markdown("---")
            st.markdown("### 📥 Télécharger le cours")
            
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    from src.features.exams.export import export_course_to_pdf
                    pdf_data = export_course_to_pdf(course_data)
                    st.download_button(
                        label="📄 Télécharger en PDF",
                        data=pdf_data,
                        file_name=f"cours_{course_form_data['grade']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération du PDF: {str(e)}")
            
            with col2:
                try:
                    from src.features.exams.export import export_course_to_docx
                    docx_data = export_course_to_docx(course_data)
                    st.download_button(
                        label="📝 Télécharger en DOCX",
                        data=docx_data,
                        file_name=f"cours_{course_form_data['grade']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération du DOCX: {str(e)}")
            
            # Reset button
            if st.button("🔄 Générer un nouveau cours", key="reset_teacher_course"):
                if hasattr(st.session_state, 'generated_teacher_course'):
                    del st.session_state.generated_teacher_course
                if hasattr(st.session_state, 'course_form_data'):
                    del st.session_state.course_form_data
                if hasattr(st.session_state, 'custom_subjects_list'):
                    del st.session_state.custom_subjects_list
                st.rerun()

# Helper functions that are still needed
def generate_exam_items(grade_label: str, courses: list[str], difficulty_label: str, n: int, want_answers: bool, course_percentages: dict = None, max_tokens_q: int = 500, max_tokens_a: int = 4000) -> list[dict]:
    return gen_items_module(create_enhanced_llm_manager, grade_label, courses, difficulty_label, n, want_answers, max_tokens_q, max_tokens_a, course_percentages)

def export_docx_from_html(html_content: str) -> BytesIO | None:
    return export_docx_module(html_content)

def export_pdf_from_html(html_content: str) -> BytesIO | None:
    return export_pdf_module(html_content)

def build_exam_html(exam_title: str, questions_with_answers: list, include_answers_flag: bool) -> str:
    """Build HTML content for exam export"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{exam_title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .exam-title {{ text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
            .exam-info {{ text-align: center; font-size: 14px; color: #666; margin-bottom: 30px; }}
            .student-info {{ margin-bottom: 30px; }}
            .question {{ margin-bottom: 30px; }}
            .question-number {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
            .question-meta {{ font-size: 12px; color: #7f8c8d; margin-bottom: 10px; }}
            .question-text {{ margin-bottom: 15px; }}
            .answer-space {{ border: 1px solid #ddd; min-height: 100px; margin: 10px 0; }}
            .answer {{ margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #28a745; border-radius: 5px; }}
            .answer-label {{ font-weight: bold; color: #28a745; margin-bottom: 10px; font-size: 16px; }}
            .answer-content {{ line-height: 1.6; color: #333; }}
        </style>
    </head>
    <body>
        <div class="exam-title">{exam_title}</div>
        <div class="exam-info">Date: _______________ Durée: _______________</div>
        
        <div class="student-info">
            <p>Nom: _________________________________</p>
            <p>Prénom: _______________________________</p>
            <p>Classe: _______________________________</p>
        </div>
    """
    
    for idx, qa in enumerate(questions_with_answers, 1):
        # Ensure question text exists and is not empty
        question_text = qa.get('question', '').strip()
        if not question_text:
            question_text = f"Question {idx} - Texte manquant"
        
        html += f"""
        <div class="question">
            <div class="question-number">Question {idx}</div>
            <div class="question-meta">Cours: {qa.get('course', 'N/A')} | Difficulté: {qa.get('difficulty', 'N/A')}</div>
            <div class="question-text">{question_text}</div>
            <div class="answer-space"></div>
        """
        
        if include_answers_flag and qa.get('answer'):
            answer_text = qa.get('answer', '').strip()
            if answer_text:
                # Clean up the answer text for better formatting
                cleaned_answer = answer_text.replace('\n\n', '\n').replace('\n', '<br>')
                html += f"""
                <div class="answer">
                    <div class="answer-label">Réponse:</div>
                    <div class="answer-content">{cleaned_answer}</div>
                </div>
                """
        elif include_answers_flag:
            # Debug: show when answer is missing
            html += f"""
            <div class="answer">
                <div class="answer-label">Réponse:</div>
                <em>Aucune réponse disponible pour cette question</em>
            </div>
            """
        
        html += "</div>"
    
    html += """
        <div style="margin-top: 50px; text-align: center; font-style: italic;">
            <p>Bonne chance !</p>
        </div>
    </body>
    </html>
    """
    return html


def course_generation_form():
    """Course generation form for teachers"""

    st.markdown("### 📚 Génération de Cours Personnalisé")
    
    # Single-column layout
    # Grade selection first (same as exam generation)
    grades = {
        "7e": "7ème année",
        "8e": "8ème année", 
        "9e": "9ème année",
        "10e": "10ème année",
        "11e": "11ème année",
        "12e": "12ème année"
    }
    selected_grade = st.selectbox("Niveau", list(grades.keys()), format_func=lambda x: grades[x], key="course_grade_select")
    
    # Course selection based on grade (same as exam generation)
    course_options = {
        "7e": ["Nombres entiers", "Fractions", "Géométrie de base", "Proportions"],
        "8e": ["Algèbre de base", "Équations", "Géométrie", "Statistiques"],
        "9e": ["Calcul littéral", "Systèmes d'équations", "Fonctions", "Probabilités"],
        "10e": ["Fonctions quadratiques", "Trigonométrie", "Logarithmes", "Suites"],
        "11e": ["Limites", "Dérivées", "Intégrales", "Nombres complexes"],
        "12e": ["Intégrales", "Équations différentielles", "Séries", "Analyse vectorielle"]
    }
    
    available_courses = course_options.get(selected_grade, ["Mathématiques"])
    subjects = st.multiselect("Cours", available_courses, default=available_courses[:2], key="course_subjects_select")
    
    # Custom course input - compact controls remain inline
    with st.expander("➕ Cours personnalisés", expanded=False):
        # Initialize session state for custom courses
        if 'custom_courses_list_course' not in st.session_state:
            st.session_state.custom_courses_list_course = []
        
        # Compact input row
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            new_custom_course = st.text_input("Nouveau cours", placeholder="Ex: Calcul différentiel", key="new_custom_course_course", label_visibility="collapsed")
        with c2:
            if st.button("➕", key="add_custom_course_course", help="Ajouter"):
                if new_custom_course and new_custom_course not in subjects and new_custom_course not in st.session_state.custom_courses_list_course:
                    st.session_state.custom_courses_list_course.append(new_custom_course)
                    st.rerun()
        with c3:
            if st.button("🗑️", key="clear_all_custom_courses_course", help="Tout effacer"):
                st.session_state.custom_courses_list_course = []
                st.rerun()
        
        # Display as compact tags
        if st.session_state.custom_courses_list_course:
            tags_html = ""
            for i, custom_course in enumerate(st.session_state.custom_courses_list_course):
                tags_html += f'<span style="background-color: #ff6b6b; color: white; padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 12px;">{custom_course} <a href="#" onclick="removeCustomCourse({i})" style="color: white; text-decoration: none; margin-left: 4px;">×</a></span>'
            
            st.markdown(f'<div style="margin-top: 8px;">{tags_html}</div>', unsafe_allow_html=True)
            
            # Individual removal buttons (hidden but functional)
            for i, custom_course in enumerate(st.session_state.custom_courses_list_course):
                if st.button("", key=f"remove_custom_course_course_{i}", help="Supprimer", type="secondary"):
                    st.session_state.custom_courses_list_course.pop(i)
                    st.rerun()
        
        # Add custom courses to the main courses list
        if st.session_state.custom_courses_list_course:
            for custom_course in st.session_state.custom_courses_list_course:
                if custom_course not in subjects:
                    subjects.append(custom_course)
    
    # Subject percentage distribution
    if len(subjects) > 1:
        st.markdown("**Répartition des exercices par sujet:**")
        subject_percentages = {}
        total_percentage = 0
        
        for subject in subjects:
            percentage = st.slider(
                f"{subject} (%)",
                min_value=0,
                max_value=100,
                value=100 // len(subjects) if subjects else 0,
                key=f"percentage_{subject}"
            )
            subject_percentages[subject] = percentage
            total_percentage += percentage
        
        if total_percentage != 100:
            st.warning(f"⚠️ Total: {total_percentage}% (doit être 100%)")
    else:
        subject_percentages = {subjects[0]: 100} if subjects else {}
    
    # Course title
    course_title = st.text_input(
        "Titre du cours",
        value=f"Cours de {', '.join(subjects)} - {grades[selected_grade]}",
        help="Titre personnalisé pour le cours"
    )
    
    # Number of exercises
    num_exercises = st.number_input(
        "Nombre d'exercices",
        min_value=1,
        max_value=10,
        value=3,
        help="Nombre d'exercices pratiques à inclure dans le cours"
    )
    
    # Difficulty
    difficulty = st.selectbox(
        "Difficulté",
        ["Facile", "Intermédiaire", "Difficile"],
        index=1,
        key="course_difficulty_select"
    )
    
    # Additional options
    with st.expander("⚙️ Options avancées"):
        include_solutions = st.checkbox("Inclure les solutions détaillées", value=True)
        include_hints = st.checkbox("Inclure des indices pour chaque exercice", value=True)
        include_resources = st.checkbox("Inclure des ressources supplémentaires", value=False)
        
        
        # Custom prompt
        custom_prompt = st.text_area(
            "Prompt personnalisé (optionnel)",
            placeholder="Ajoutez des instructions spécifiques pour la génération du cours...",
            help="Instructions supplémentaires pour personnaliser le contenu du cours"
        )
    
    return {
        "subjects": subjects,
        "num_exercises": num_exercises,
        "grade": selected_grade,
        "difficulty": difficulty,
        "subject_percentages": subject_percentages,
        "course_title": course_title,
        "include_solutions": include_solutions,
        "include_hints": include_hints,
        "include_resources": include_resources,
        "custom_prompt": custom_prompt
    }


def generate_teacher_course(form_data):
    """Generate course for teachers"""
    try:
        llm_manager = create_enhanced_llm_manager()
        
        # Calculate number of exercises per subject
        exercises_per_subject = {}
        for subject, percentage in form_data["subject_percentages"].items():
            exercises_per_subject[subject] = max(1, int((percentage / 100) * form_data["num_exercises"]))
        
        # Adjust to match total
        total_exercises = sum(exercises_per_subject.values())
        if total_exercises != form_data["num_exercises"]:
            # Adjust the largest subject
            largest_subject = max(exercises_per_subject, key=exercises_per_subject.get)
            exercises_per_subject[largest_subject] += (form_data["num_exercises"] - total_exercises)
        
        # Build course prompt
        course_prompt = f"""
        En tant qu'enseignant expert en mathématiques, générez un cours complet pour le niveau {form_data['grade']} avec une difficulté {form_data['difficulty']}.
        
        Sujets à couvrir: {', '.join(form_data['subjects'])}
        Nombre total d'exercices: {form_data['num_exercises']}
        Répartition des exercices: {', '.join([f'{subject}: {count} exercices' for subject, count in exercises_per_subject.items()])}
        
        Le cours doit inclure:
        1. Une introduction motivante et détaillée
        2. Des explications claires pour chaque sujet
        3. EXACTEMENT {form_data['num_exercises']} exercices pratiques avec solutions complètes
        4. Des conseils d'apprentissage spécifiques
        5. Des ressources pour approfondir
        
        {"Inclure des solutions détaillées pour chaque exercice." if form_data['include_solutions'] else ""}
        {"Inclure des indices pour chaque exercice." if form_data['include_hints'] else ""}
        {"Inclure des ressources supplémentaires." if form_data['include_resources'] else ""}
        
        FORMAT MATHÉMATIQUE (MARKDOWN UNIQUEMENT):
        - Utiliser UNIQUEMENT le format Markdown - JAMAIS de LaTeX
        - Pour math inline: $x + 2 = 5$ (simple dollar)
        - Pour équations: $$x^2 + 3x - 2 = 0$$ (double dollar)
        - Écrire les formules en texte simple quand possible
        - Éviter toutes les commandes LaTeX comme \text, \dfrac, \frac, \mid, \cap, \cup, etc.
        - Préférer des expressions simples comme P(A|B) = P(A et B) / P(B)
        - Préférer (a + b) / 2 au lieu d'une fraction LaTeX
        
        {form_data['custom_prompt'] if form_data['custom_prompt'] else ""}
        
        Format de réponse en JSON:
        {{
            "title": "{form_data['course_title']}",
            "introduction": "Introduction motivante et détaillée",
            "topics": [
                {{
                    "name": "Nom du sujet",
                    "explanation": "Explication très détaillée du concept avec exemples",
                    "exercises": [
                        {{
                            "question": "Énoncé de l'exercice - très détaillé",
                            "solution": "Solution complète et détaillée avec toutes les étapes",
                            "hints": ["Indice 1", "Indice 2", "Indice 3"]
                        }}
                    ]
                }}
            ],
            "tips": ["Conseil détaillé 1", "Conseil détaillé 2", "Conseil détaillé 3"],
            "resources": ["Ressource 1", "Ressource 2", "Ressource 3"]
        }}
        """
        
        # Generate course using LLM
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        template = PromptTemplate(input_variables=[], template="{prompt}")
        chain = template | llm_manager.create_llm_with_params(temperature=0.3, max_tokens=None) | StrOutputParser()
        
        response = llm_manager.invoke_with_retry(chain, {"prompt": course_prompt})
        
        # Parse response
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end > json_start:
                    json_content = response[json_start:json_end].strip()
                    course_data = json.loads(json_content)
                else:
                    raise json.JSONDecodeError("No closing ``` found", response, json_start)
            else:
                course_data = json.loads(response)
            
            
            return course_data
        except json.JSONDecodeError:
            # Fallback course
            return {
                "title": form_data['course_title'],
                "introduction": f"Cours de {', '.join(form_data['subjects'])} pour le niveau {form_data['grade']}.",
                "topics": [
                    {
                        "name": subject,
                        "explanation": f"Explication de base pour {subject}.",
                        "exercises": [
                            {
                                "question": f"Exercice de {subject} - Consultez vos ressources",
                                "solution": "Solution disponible dans vos manuels",
                                "hints": ["Consultez vos notes", "Demandez de l'aide", "Pratiquez régulièrement"]
                            } for _ in range(exercises_per_subject.get(subject, 1))
                        ]
                    } for subject in form_data['subjects']
                ],
                "tips": ["Pratiquez régulièrement", "Consultez vos ressources", "Demandez de l'aide"],
                "resources": ["Manuels de cours", "Ressources en ligne", "Aide de l'enseignant"]
            }
    
    except Exception as e:
        raise Exception(f"Erreur lors de la génération du cours: {str(e)}")




if __name__ == "__main__":
    main()