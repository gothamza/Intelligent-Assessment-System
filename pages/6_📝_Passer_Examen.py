import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys
import re

# Ensure src is importable
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.enhanced_chains import create_enhanced_llm_manager
from src.features.feedback.classification import process_exam_results
from src.features.exams.session import (
    format_time,
    start_exam_timer,
    update_timer,
)

st.set_page_config(page_title="Passer un Examen", layout="wide")

# ---------- Helpers ----------

def load_exam_from_json(json_text: str):
    """Load exam from JSON text"""
    try:
        exam = json.loads(json_text)
        assert isinstance(exam, dict)
        assert "title" in exam and "questions" in exam
        assert isinstance(exam["questions"], list)
        return exam, None
    except Exception as e:
        return None, f"Format d'examen invalide: {e}"


def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text, None
    except ImportError:
        return None, "PyPDF2 n'est pas installé. Veuillez installer: pip install PyPDF2"
    except Exception as e:
        return None, f"Erreur lors de la lecture du PDF: {str(e)}"


def extract_text_from_docx(uploaded_file):
    """Extract text from Word document"""
    try:
        from docx import Document
        doc = Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text, None
    except ImportError:
        return None, "python-docx n'est pas installé. Veuillez installer: pip install python-docx"
    except Exception as e:
        return None, f"Erreur lors de la lecture du DOCX: {str(e)}"


def parse_questions_from_text(text: str, title: str = "Examen Importé") -> dict:
    """
    Parse questions from plain text using pattern matching.
    Supports formats like:
    - Question 1
      Cours: ... | Difficulté: ...
      Actual question text...
    - Question 1: ...
    - 1. ...
    """
    questions = []
    
    # Try to extract title and duration from document header
    lines = text.strip().split('\n')
    exam_title = title
    exam_duration = None
    
    # Look for title in first few lines
    if lines and (lines[0].strip().lower().startswith(('examen', 'test', 'contrôle', 'évaluation'))):
        exam_title = lines[0].strip()
        text = '\n'.join(lines[1:])
    
    # Try to extract duration from header (common patterns)
    # Patterns: "Durée: 60 minutes", "Duration: 1h30", "Temps: 2 heures"
    duration_patterns = [
        r'Durée\s*:\s*([^_\n]+)',
        r'Duration\s*:\s*([^_\n]+)',
        r'Temps\s*:\s*([^_\n]+)',
        r'Time\s*:\s*([^_\n]+)',
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            exam_duration = match.group(1).strip()
            # Clean up underscores and extra spaces
            exam_duration = re.sub(r'_+', '', exam_duration).strip()
            if exam_duration:
                break
    
    # Pattern for question blocks - only match "Question N" followed by "Cours:" metadata
    # This ensures we only capture actual questions, not header info
    question_pattern = re.compile(
        r'Question\s+(\d+)\s*\n\s*Cours:\s*([^|\n]+)\s*\|\s*Difficulté:\s*([^\n]+)\s*\n(.+?)(?=\n\s*Question\s+\d+|$)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    
    matches = question_pattern.finditer(text)
    
    for match in matches:
        question_num = match.group(1)
        course = match.group(2).strip()
        difficulty = match.group(3).strip()
        block_text = match.group(4).strip()
        
        # Clean the question text
        question_text = block_text
        
        # Remove answer lines (lines with only underscores)
        question_text = re.sub(r'^\s*_{3,}\s*$', '', question_text, flags=re.MULTILINE).strip()
        
        # Remove empty lines
        question_text = '\n'.join([line.strip() for line in question_text.split('\n') if line.strip() and not line.strip().startswith('_')])
        
        # If question is still too short or just underscores, skip it
        if not question_text or len(question_text) < 10 or question_text.replace('_', '').strip() == '':
            continue
        
        questions.append({
            "course": course,
            "difficulty": difficulty,
            "question": question_text
        })
    
    # If no questions found with "Question N" pattern, try numbered format (1., 2., etc.)
    if not questions:
        numbered_pattern = re.compile(
            r'^(\d+)[\.\)]\s*(.+?)(?=^\d+[\.\)]|$)',
            re.MULTILINE | re.DOTALL
        )
        
        numbered_matches = numbered_pattern.finditer(text)
        
        for match in numbered_matches:
            question_text = match.group(2).strip()
            
            if question_text and len(question_text) > 10:
                # Extract course if mentioned
                course = "Mathématiques"
                if 'Cours:' in question_text:
                    course_match = re.search(r'Cours:\s*([^|\n]+)', question_text)
                    if course_match:
                        course = course_match.group(1).strip()
                        question_text = re.sub(r'Cours:.*?\n', '', question_text).strip()
                
                questions.append({
                    "course": course,
                    "difficulty": "Intermédiaire",
                    "question": question_text
                })
    
    # Fallback: split by double newlines
    if not questions:
        potential_questions = [q.strip() for q in text.split('\n\n') if q.strip() and len(q.strip()) > 20]
        for q_text in potential_questions[:20]:  # Limit to 20 questions
            if q_text:
                questions.append({
                    "course": "Mathématiques",
                    "difficulty": "Intermédiaire",
                    "question": q_text
                })
    
    # Use extracted duration if found, otherwise calculate based on number of questions
    if not exam_duration or exam_duration == "":
        exam_duration = f"{len(questions) * 5} minutes"  # 5 min per question as default
    
    return {
        "title": exam_title,
        "subtitle": "Examen importé depuis fichier",
        "duration": exam_duration,
        "instructions": "Répondez clairement à chaque question. Justifiez vos étapes lorsque c'est nécessaire.",
        "questions": questions
    }


def extract_questions_with_llm(text: str, llm_manager) -> dict:
    """Use LLM to extract questions from text"""
    prompt = f"""
    Analysez le texte suivant et extrayez toutes les questions d'examen de mathématiques.
    
    Texte:
    {text[:4000]}  # Limit text length
    
    Retournez un JSON avec ce format:
    {{
        "title": "Titre de l'examen",
        "duration": "60 minutes",
        "questions": [
            {{
                "course": "Algèbre/Géométrie/etc",
                "difficulty": "Facile/Intermédiaire/Difficile",
                "question": "Texte complet de la question"
            }}
        ]
    }}
    
    IMPORTANT:
    - Cherchez dans l'en-tête du document pour la durée (Durée:, Duration:, Temps:)
    - Si la durée n'est pas mentionnée, laissez le champ vide ""
    - N'incluez que les questions de mathématiques
    - Ignorez les instructions, champs de réponse vides, etc.
    """
    
    try:
        chat = llm_manager.get_default_chat()
        response = chat.invoke([{"role": "user", "content": prompt}])
        response_text = response if isinstance(response, str) else str(response)
        
        # Parse JSON response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_content = response_text[json_start:json_end].strip()
            data = json.loads(json_content)
        else:
            data = json.loads(response_text)
        
        # Add default fields
        data.setdefault("subtitle", "Examen importé")
        
        # Use extracted duration or calculate based on number of questions
        if not data.get("duration") or data.get("duration") == "":
            data["duration"] = f"{len(data.get('questions', [])) * 5} minutes"
        
        data.setdefault("instructions", "Répondez clairement. Justifiez vos étapes.")
        
        return data
    except Exception as e:
        st.warning(f"Extraction LLM échouée: {e}. Utilisation du parser de base.")
        return parse_questions_from_text(text)


def example_exam() -> dict:
    return {
        "title": "Examen de Mathématiques - Algèbre et Géométrie",
        "subtitle": "Évaluation de mi-semestre",
        "duration": "45 minutes",
        "instructions": "Répondez clairement. Justifiez vos étapes lorsque c'est nécessaire.",
        "questions": [
            {
                "course": "Algèbre",
                "difficulty": "Intermédiaire",
                "question": "Résoudre l'équation: 2x + 5 = 17."
            },
            {
                "course": "Géométrie",
                "difficulty": "Facile",
                "question": "Calculez le périmètre d'un rectangle de longueur 8 cm et de largeur 3 cm."
            },
            {
                "course": "Fonctions",
                "difficulty": "Difficile",
                "question": "Soit f(x) = x^2 - 4x + 3. Trouvez les zéros de f."
            }
        ]
    }


def generate_course_from_results(llm_manager, exam, classifications, individual_feedbacks):
    """Generate a personalized study plan based on exam results"""
    topics = {}
    for i, q in enumerate(exam.get("questions", [])):
        course_name = q.get("course", "Général")
        topics.setdefault(course_name, {"correct": 0, "partial": 0, "incorrect": 0, "items": []})
        label = (classifications[i] if i < len(classifications) else "inconnu").lower()
        if "part" in label:
            topics[course_name]["partial"] += 1
        elif "inc" in label:
            topics[course_name]["incorrect"] += 1
        else:
            topics[course_name]["correct"] += 1
        topics[course_name]["items"].append({
            "question": q.get("question", ""),
            "feedback": individual_feedbacks[i] if i < len(individual_feedbacks) else ""
        })

    # Build prompt for course generation - escape braces by doubling them
    topics_json = json.dumps(topics, ensure_ascii=False, indent=2)
    
    # Create the prompt text - no template variables needed
    prompt_text = f"""Tu es un professeur de mathématiques bienveillant. 
À partir des résultats d'un examen, propose un mini-plan de cours personnalisé (3-6 points) 
avec des explications courtes et 1 ressource utile par point (lien web de référence générale). 
Reste concis et structuré.

**Titre de l'examen:** {exam.get("title")}

**Résultats par sujet:**
{topics_json}

**Format attendu:**
Structure ton plan avec des titres clairs et des points numérotés.
Pour chaque sujet à améliorer, propose:
1. Un concept clé à revoir
2. Une explication courte (2-3 phrases)
3. Un lien vers une ressource en ligne (Khan Academy, Alloprof, etc.)
"""

    try:
        # Use direct LLM invocation instead of PromptTemplate to avoid variable parsing issues
        llm = llm_manager.create_llm_with_params(temperature=0.7, max_tokens=1500)
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": "Tu es un professeur de mathématiques bienveillant et expert."},
            {"role": "user", "content": prompt_text}
        ]
        
        # Invoke the LLM directly
        response = llm.invoke(messages)
        
        # Extract content from response
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
            
    except Exception as e:
        return f"**Impossible de générer le cours:** {str(e)}\n\n**Suggestion:** Vérifiez vos clés API dans le fichier .env"


# ---------- UI ----------

st.title("📝 Passer un Examen")

st.markdown("""
Chargez un examen depuis un fichier (JSON, PDF, ou Word) ou utilisez l'exemple fourni pour démarrer.
""")

# File type info
with st.expander("ℹ️ Formats de fichiers supportés", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📄 JSON (Recommandé)**")
        st.code(json.dumps({
            "title": "Examen ...",
            "subtitle": "...",
            "duration": "45 minutes",
            "instructions": "...",
            "questions": [
                {"course": "Algèbre", "difficulty": "Facile", "question": "..."}
            ]
        }, indent=2, ensure_ascii=False), language="json")
    
    with col2:
        st.markdown("**📄 PDF**")
        st.info("""
        Format attendu:
        - Question 1: ...
        - Question 2: ...
        ou
        - 1. ...
        - 2. ...
        """)
    
    with col3:
        st.markdown("**📝 Word (DOCX)**")
        st.info("""
        Format attendu:
        - Question 1: ...
        - Question 2: ...
        ou
        - 1. ...
        - 2. ...
        """)

# File upload section
col_u1, col_u2, col_u3 = st.columns([3, 1, 1])
with col_u1:
    uploaded = st.file_uploader(
        "📁 Uploader un fichier d'examen", 
        type=["json", "pdf", "docx", "doc"],
        help="Accepte les fichiers JSON, PDF, et Word (DOCX)"
    )
with col_u2:
    use_llm_extraction = st.checkbox(
        "🤖 Extraction AI",
        value=False,
        help="Utiliser l'IA pour extraire les questions (recommandé pour PDF/Word complexes)"
    )
with col_u3:
    use_example = st.button("📋 Utiliser l'exemple", use_container_width=True)

# Tip for users
if uploaded is None and not use_example:
    st.info("💡 **Astuce:** Pour les fichiers PDF/Word avec format complexe, cochez '🤖 Extraction AI' pour de meilleurs résultats.")

if "exam_data" not in st.session_state:
    st.session_state.exam_data = None
if "student_answers" not in st.session_state:
    st.session_state.student_answers = {}
if "exam_completed" not in st.session_state:
    st.session_state.exam_completed = False
if "result_payload" not in st.session_state:
    st.session_state.result_payload = None
if "loaded_file_name" not in st.session_state:
    st.session_state.loaded_file_name = None

# Load exam
if use_example:
    st.session_state.exam_data = example_exam()
    st.session_state.student_answers = {}
    st.session_state.exam_completed = False
    st.session_state.result_payload = None
    st.session_state.loaded_file_name = "example"
    st.rerun()

elif uploaded is not None:
    file_extension = uploaded.name.split('.')[-1].lower()
    
    # Only process if this is a new file (not already loaded)
    if st.session_state.loaded_file_name != uploaded.name:
        with st.spinner(f"📖 Lecture du fichier {file_extension.upper()}..."):
            try:
                if file_extension == 'json':
                    # JSON file - direct parsing
                    text = uploaded.read().decode("utf-8")
                    exam, err = load_exam_from_json(text)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.exam_data = exam
                        st.session_state.student_answers = {}
                        st.session_state.exam_completed = False
                        st.session_state.result_payload = None
                        st.session_state.loaded_file_name = uploaded.name
                        st.success(f"✅ Examen JSON chargé: {len(exam.get('questions', []))} questions")
                        st.rerun()
                
                elif file_extension == 'pdf':
                    # PDF file - extract text then parse
                    text, err = extract_text_from_pdf(uploaded)
                    if err:
                        st.error(err)
                    else:
                        # Show preview
                        with st.expander("📄 Aperçu du texte extrait (premiers 500 caractères)"):
                            st.text(text[:500])
                        
                        # Extract questions
                        if use_llm_extraction:
                            llm_manager = create_enhanced_llm_manager()
                            exam = extract_questions_with_llm(text, llm_manager)
                        else:
                            exam = parse_questions_from_text(text, uploaded.name)
                        
                        if exam.get('questions'):
                            st.session_state.exam_data = exam
                            st.session_state.student_answers = {}
                            st.session_state.exam_completed = False
                            st.session_state.result_payload = None
                            st.session_state.loaded_file_name = uploaded.name
                            st.success(f"✅ {len(exam['questions'])} questions extraites du PDF")
                            st.rerun()
                        else:
                            st.error("❌ Aucune question trouvée dans le PDF. Vérifiez le format.")
                
                elif file_extension in ['docx', 'doc']:
                    # Word file - extract text then parse
                    text, err = extract_text_from_docx(uploaded)
                    if err:
                        st.error(err)
                    else:
                        # Show preview
                        with st.expander("📄 Aperçu du texte extrait (premiers 500 caractères)"):
                            st.text(text[:500])
                        
                        # Extract questions
                        if use_llm_extraction:
                            llm_manager = create_enhanced_llm_manager()
                            exam = extract_questions_with_llm(text, llm_manager)
                        else:
                            exam = parse_questions_from_text(text, uploaded.name)
                        
                        if exam.get('questions'):
                            st.session_state.exam_data = exam
                            st.session_state.student_answers = {}
                            st.session_state.exam_completed = False
                            st.session_state.result_payload = None
                            st.session_state.loaded_file_name = uploaded.name
                            st.success(f"✅ {len(exam['questions'])} questions extraites du Word")
                            st.rerun()
                        else:
                            st.error("❌ Aucune question trouvée dans le document. Vérifiez le format.")
            
            except Exception as e:
                st.error(f"❌ Erreur lors du traitement du fichier: {str(e)}")

exam = st.session_state.exam_data

if not exam:
    st.info("Aucun examen chargé. Uploadez un JSON ou utilisez l'exemple.")
    st.stop()

# Display exam meta
st.header(f"📚 {exam.get('title', 'Examen')}")
if exam.get("subtitle"):
    st.subheader(exam["subtitle"]) 

meta1, meta2, meta3 = st.columns(3)
with meta1:
    st.info(f"📊 Questions: {len(exam.get('questions', []))}")
with meta2:
    st.info(f"⏱️ Durée: {exam.get('duration', 'Non limitée')}")
with meta3:
    st.info(f"🗓️ Date: {datetime.now().strftime('%d/%m/%Y')}")

if exam.get("instructions"):
    with st.expander("📋 Instructions"):
        st.write(exam["instructions"])

# Timer (best-effort)
if "exam_start_time" not in st.session_state:
    # Try to parse minutes from duration
    duration_text = (exam.get("duration") or "").lower()
    minutes = 0
    if "minute" in duration_text:
        try:
            minutes = int("".join([c for c in duration_text if c.isdigit()]))
        except Exception:
            minutes = 0
    elif "heure" in duration_text or "hour" in duration_text:
        try:
            hours = int("".join([c for c in duration_text if c.isdigit()]))
            minutes = hours * 60
        except Exception:
            minutes = 0
    start_exam_timer(minutes if minutes > 0 else None)

update_timer()
if st.session_state.time_remaining is not None:
    color = (
        "red" if st.session_state.time_remaining < 300 else
        "orange" if st.session_state.time_remaining < 900 else
        "green"
    )
    st.markdown(f"""
    <div style="text-align:center;padding:20px;background:#f0f2f6;border-radius:10px;margin:20px 0;">
        <h2 style="color:{color};margin:0;">⏰ Temps restant: {format_time(int(st.session_state.time_remaining))}</h2>
    </div>
    """, unsafe_allow_html=True)

# Questions
if not st.session_state.exam_completed:
    st.header("📝 Questions de l'Examen")
    for i, q in enumerate(exam.get("questions", [])):
        with st.container():
            st.markdown(f"### Question {i+1}")
            st.markdown(f"**Cours:** {q.get('course','N/A')} | **Difficulté:** {q.get('difficulty','N/A')}")
            st.markdown(f"**Énoncé:** {q.get('question','')}")

            ans_key = f"answer_{i}"
            current = st.session_state.student_answers.get(str(i), "")
            value = st.text_area(
                "Votre réponse:",
                value=current,
                height=150,
                key=ans_key,
            )
            if value:
                st.session_state.student_answers[str(i)] = value
            st.divider()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("✅ Soumettre l'Examen", type="primary", use_container_width=True):
            st.session_state.exam_completed = True
            st.rerun()

# Results
if st.session_state.exam_completed:
    st.header("🎉 Examen Terminé!")

    # Generate AI feedback
    with st.spinner("🤖 Génération du feedback en cours..."):
        try:
            llm_manager = create_enhanced_llm_manager()
            classifications, individual_feedbacks, score, overall_feedback = process_exam_results(
                llm_manager,
                exam.get("questions", []),
                st.session_state.student_answers
            )
            st.session_state.result_payload = {
                "classifications": classifications,
                "individual_feedbacks": individual_feedbacks,
                "score": score,
                "overall_feedback": overall_feedback,
            }
        except Exception as e:
            st.error(f"Erreur lors de la génération du feedback: {e}")
            st.stop()

    payload = st.session_state.result_payload or {}

    score = float(payload.get("score", 0))
    color = "green" if score >= 70 else ("orange" if score >= 50 else "red")
    st.markdown(f"""
    <div style="text-align:center;padding:20px;background:#f0f2f6;border-radius:10px;margin:20px 0;">
        <h2 style="color:{color};margin:0;">🎯 Score: {score:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    if payload.get("classifications"):
        st.subheader("📝 Feedback par Question")
        for i, q in enumerate(exam.get("questions", [])):
            if i < len(payload["classifications"]):
                label = payload["classifications"][i]
                answer_txt = st.session_state.student_answers.get(str(i), "")
                with st.expander(f"Question {i+1} - {label.title()}"):
                    st.markdown(f"**Question:** {q.get('question','')}")
                    st.markdown(f"**Votre réponse:** {answer_txt}")
                    if payload.get("individual_feedbacks") and i < len(payload["individual_feedbacks"]):
                        st.markdown(f"**Feedback:** {payload['individual_feedbacks'][i]}")

    if payload.get("overall_feedback"):
        st.subheader("💬 Feedback Global")
        st.info(str(payload["overall_feedback"]))

    st.markdown("---")
    
    # Download results section
    st.subheader("💾 Télécharger les résultats")
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        # Download exam with answers as JSON
        exam_with_answers = {
            "title": exam.get("title", "Examen"),
            "subtitle": exam.get("subtitle", ""),
            "duration": exam.get("duration", ""),
            "instructions": exam.get("instructions", ""),
            "date_completed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": payload.get("score", 0),
            "questions_and_answers": [
                {
                    "question_number": i + 1,
                    "course": q.get("course", ""),
                    "difficulty": q.get("difficulty", ""),
                    "question": q.get("question", ""),
                    "student_answer": st.session_state.student_answers.get(str(i), ""),
                    "classification": payload["classifications"][i] if i < len(payload.get("classifications", [])) else "N/A",
                    "feedback": payload["individual_feedbacks"][i] if i < len(payload.get("individual_feedbacks", [])) else ""
                }
                for i, q in enumerate(exam.get("questions", []))
            ],
            "overall_feedback": payload.get("overall_feedback", "")
        }
        
        st.download_button(
            label="📄 Télécharger JSON",
            data=json.dumps(exam_with_answers, ensure_ascii=False, indent=2),
            file_name=f"resultat_examen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            help="Télécharger les résultats complets en format JSON"
        )
    
    with col_d2:
        # Download exam without answers (for retake)
        exam_template = {
            "title": exam.get("title", "Examen"),
            "subtitle": exam.get("subtitle", ""),
            "duration": exam.get("duration", ""),
            "instructions": exam.get("instructions", ""),
            "questions": [
                {
                    "course": q.get("course", ""),
                    "difficulty": q.get("difficulty", ""),
                    "question": q.get("question", "")
                }
                for q in exam.get("questions", [])
            ]
        }
        
        st.download_button(
            label="📋 Télécharger Examen",
            data=json.dumps(exam_template, ensure_ascii=False, indent=2),
            file_name=f"examen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            help="Télécharger l'examen vierge (sans vos réponses)"
        )
    
    with col_d3:
        # Simple text export
        text_results = f"""
Résultats de l'Examen
====================
Titre: {exam.get('title', 'Examen')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Score: {payload.get('score', 0):.1f}%

Questions et Réponses:
{"="*50}

"""
        for i, q in enumerate(exam.get("questions", [])):
            text_results += f"""
Question {i+1}: {q.get('question', '')}
Votre réponse: {st.session_state.student_answers.get(str(i), '')}
Classification: {payload['classifications'][i] if i < len(payload.get('classifications', [])) else 'N/A'}
Feedback: {payload['individual_feedbacks'][i] if i < len(payload.get('individual_feedbacks', [])) else ''}

{'='*50}

"""
        
        st.download_button(
            label="📝 Télécharger TXT",
            data=text_results,
            file_name=f"resultat_examen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            help="Télécharger les résultats en format texte"
        )
    
    st.markdown("---")
    st.subheader("📚 Générer un mini-cours personnalisé avec ressources")
    if st.button("📘 Générer le cours"):
        with st.spinner("Génération du cours en cours..."):
            llm_manager = create_enhanced_llm_manager()
            course_md = generate_course_from_results(
                llm_manager,
                exam,
                payload.get("classifications", []),
                payload.get("individual_feedbacks", []),
            )
        st.markdown(course_md)

    # Actions
    st.markdown("---")
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("🏠 Accueil", use_container_width=True):
            st.switch_page("main.py")
    with a2:
        if st.button("🔄 Nouvel Examen", use_container_width=True):
            for key in [
                "exam_data", "student_answers", "exam_completed", "result_payload",
                "exam_start_time", "exam_duration", "time_remaining", "loaded_file_name"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    with a3:
        if st.button("📝 Créer un Examen", use_container_width=True):
            st.switch_page("pages/6_📝_Création_d_Examens.py")
