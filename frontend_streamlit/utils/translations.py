"""
Translation system for Streamlit interface
Provides translations for UI text based on selected language
"""

TRANSLATIONS = {
    "Français": {
        # Exam Generation Page
        "exam_generation": {
            "title": "Création d'Examen",
            "subtitle": "Générez un examen personnalisé avec une répartition par cours.",
            "course_selection": "Sélection des Cours",
            "no_courses": "Aucun cours disponible pour",
            "select_courses": "Choisissez les cours à inclure dans l'examen:",
            "course_percentage": "Répartition par Cours",
            "percentage_mode_auto": "Automatique (égale)",
            "percentage_mode_manual": "Manuelle (personnalisée)",
            "auto_normalize": "Auto-normaliser à 100%",
            "total_percentage": "Total",
            "must_be_100": "doit être 100%",
            "perfect": "Parfait!",
            "preview_distribution": "Aperçu de la répartition:",
            "exam_settings": "Paramètres de l'Examen",
            "difficulty": "Difficulté:",
            "exam_title": "Titre de l'examen:",
            "include_answers": "Inclure les réponses",
            "generate_exam": "Générer l'Examen",
            "error_percentage": "La somme des pourcentages doit être égale à 100%",
            "generated_exam": "Examen Généré",
            "subject": "Matière:",
            "grade": "Niveau:",
            "num_questions": "Nombre de questions:",
            "course": "Cours:",
            "question": "Question:",
            "answer": "Réponse:",
            "download_exam": "Télécharger l'Examen",
            "download_json": "JSON",
            "download_pdf": "PDF",
            "download_word": "Word",
            "take_exam": "Passer l'Examen",
            "generating": "Génération de l'examen en cours...",
            "exam_saved": "Examen sauvegardé! Allez à la page 'Passer un Examen' pour commencer.",
            "use_navigation": "Utilisez la navigation latérale pour accéder à la page 'Passer un Examen'.",
            "raw_response": "Réponse brute de l'IA:",
        },
        # Exam Taking Page
        "exam_taking": {
            "title": "Passer un Examen",
            "subtitle": "Répondez aux questions de l'examen et recevez un feedback détaillé après soumission.",
            "load_exam": "Charger un Examen",
            "available_from_generation": "Un examen est disponible depuis la page de génération.",
            "load_available": "Charger l'examen disponible",
            "upload_file": "Ou téléchargez un fichier d'examen (JSON, PDF, DOCX):",
            "upload_help": "Téléchargez un fichier JSON, PDF ou Word contenant un examen",
            "questions_title": "Questions de l'Examen",
            "num_questions_label": "Nombre de questions:",
            "your_answer": "Votre réponse:",
            "submit_exam": "Soumettre l'Examen",
            "exam_completed": "Examen Terminé!",
            "score_final": "Score Final",
            "feedback_per_question": "Feedback par Question",
            "your_response": "Votre réponse:",
            "classification": "Classification:",
            "feedback": "Feedback:",
            "overall_feedback": "Feedback Global",
            "download_results": "Télécharger les Résultats",
            "download_json": "JSON",
            "download_pdf": "PDF",
            "download_word": "Word",
            "new_exam": "Nouvel Examen",
            "extracting_pdf": "Extraction du texte depuis le PDF...",
            "extracting_docx": "Extraction du texte depuis le document Word...",
            "analyzing": "Analyse des questions...",
            "preview_text": "Aperçu du texte extrait (premiers 500 caractères)",
            "success_json": "Examen chargé avec succès depuis le fichier JSON!",
            "success_pdf": "question(s) extraite(s) du PDF!",
            "success_docx": "question(s) extraite(s) du document Word!",
            "error_invalid_format": "Format d'examen invalide. Le fichier doit contenir une liste 'questions'.",
            "error_no_questions": "Aucune question trouvée. Vérifiez le format du document.",
            "expected_format": "Le format attendu est: 'Question N\\nCours: ... | Difficulté: ...\\nTexte de la question...'",
        },
        # Common
        "common": {
            "difficulty_easy": "Facile",
            "difficulty_intermediate": "Intermédiaire",
            "difficulty_hard": "Difficile",
            "loading": "Chargement...",
            "error": "Erreur",
            "success": "Succès",
            "warning": "Avertissement",
            "info": "Information",
        }
    },
    "English": {
        # Exam Generation Page
        "exam_generation": {
            "title": "Exam Generation",
            "subtitle": "Generate a personalized exam with course distribution.",
            "course_selection": "Course Selection",
            "no_courses": "No courses available for",
            "select_courses": "Choose courses to include in the exam:",
            "course_percentage": "Course Distribution",
            "percentage_mode_auto": "Automatic (equal)",
            "percentage_mode_manual": "Manual (customized)",
            "auto_normalize": "Auto-normalize to 100%",
            "total_percentage": "Total",
            "must_be_100": "must be 100%",
            "perfect": "Perfect!",
            "preview_distribution": "Distribution preview:",
            "exam_settings": "Exam Settings",
            "difficulty": "Difficulty:",
            "exam_title": "Exam title:",
            "include_answers": "Include answers",
            "generate_exam": "Generate Exam",
            "error_percentage": "The sum of percentages must equal 100%",
            "generated_exam": "Generated Exam",
            "subject": "Subject:",
            "grade": "Grade:",
            "num_questions": "Number of questions:",
            "course": "Course:",
            "question": "Question:",
            "answer": "Answer:",
            "download_exam": "Download Exam",
            "download_json": "JSON",
            "download_pdf": "PDF",
            "download_word": "Word",
            "take_exam": "Take Exam",
            "generating": "Generating exam...",
            "exam_saved": "Exam saved! Go to the 'Take Exam' page to start.",
            "use_navigation": "Use the sidebar navigation to access the 'Take Exam' page.",
            "raw_response": "Raw AI response:",
            "exam_generated": "Exam generated successfully!",
            "error_extract": "Unable to extract questions. Please try again with a clearer prompt.",
            "error_parse": "Error parsing JSON:",
        },
        # Exam Taking Page
        "exam_taking": {
            "title": "Take an Exam",
            "subtitle": "Answer the exam questions and receive detailed feedback after submission.",
            "load_exam": "Load an Exam",
            "available_from_generation": "An exam is available from the generation page.",
            "load_available": "Load available exam",
            "upload_file": "Or upload an exam file (JSON, PDF, DOCX):",
            "upload_help": "Upload a JSON, PDF or Word file containing an exam",
            "questions_title": "Exam Questions",
            "num_questions_label": "Number of questions:",
            "your_answer": "Your answer:",
            "submit_exam": "Submit Exam",
            "exam_completed": "Exam Completed!",
            "score_final": "Final Score",
            "feedback_per_question": "Feedback per Question",
            "your_response": "Your response:",
            "classification": "Classification:",
            "feedback": "Feedback:",
            "overall_feedback": "Overall Feedback",
            "download_results": "Download Results",
            "download_json": "JSON",
            "download_pdf": "PDF",
            "download_word": "Word",
            "new_exam": "New Exam",
            "extracting_pdf": "Extracting text from PDF...",
            "extracting_docx": "Extracting text from Word document...",
            "analyzing": "Analyzing questions...",
            "preview_text": "Extracted text preview (first 500 characters)",
            "success_json": "Exam loaded successfully from JSON file!",
            "success_pdf": "question(s) extracted from PDF!",
            "success_docx": "question(s) extracted from Word document!",
            "error_invalid_format": "Invalid exam format. The file must contain a 'questions' list.",
            "error_no_questions": "No questions found. Check the document format.",
            "expected_format": "Expected format: 'Question N\\nCourse: ... | Difficulty: ...\\nQuestion text...'",
        },
        # Common
        "common": {
            "difficulty_easy": "Easy",
            "difficulty_intermediate": "Intermediate",
            "difficulty_hard": "Hard",
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            "warning": "Warning",
            "info": "Information",
        }
    },
    "العربية": {
        # Exam Generation Page
        "exam_generation": {
            "title": "إنشاء امتحان",
            "subtitle": "أنشئ امتحانًا مخصصًا مع توزيع حسب المادة.",
            "course_selection": "اختيار المواد",
            "no_courses": "لا توجد مواد متاحة لـ",
            "select_courses": "اختر المواد المراد تضمينها في الامتحان:",
            "course_percentage": "توزيع المواد",
            "percentage_mode_auto": "تلقائي (متساوٍ)",
            "percentage_mode_manual": "يدوي (مخصص)",
            "auto_normalize": "تطبيع تلقائي إلى 100%",
            "total_percentage": "الإجمالي",
            "must_be_100": "يجب أن يكون 100%",
            "perfect": "مثالي!",
            "preview_distribution": "معاينة التوزيع:",
            "exam_settings": "إعدادات الامتحان",
            "difficulty": "الصعوبة:",
            "exam_title": "عنوان الامتحان:",
            "include_answers": "تضمين الإجابات",
            "generate_exam": "إنشاء الامتحان",
            "error_percentage": "يجب أن يكون مجموع النسب المئوية 100%",
            "generated_exam": "الامتحان المُنشأ",
            "subject": "المادة:",
            "grade": "المستوى:",
            "num_questions": "عدد الأسئلة:",
            "course": "المادة:",
            "question": "السؤال:",
            "answer": "الإجابة:",
            "download_exam": "تحميل الامتحان",
            "download_json": "JSON",
            "download_pdf": "PDF",
            "download_word": "Word",
            "take_exam": "أداء الامتحان",
            "generating": "جارٍ إنشاء الامتحان...",
        },
        # Exam Taking Page
        "exam_taking": {
            "title": "أداء امتحان",
            "subtitle": "أجب على أسئلة الامتحان واحصل على ملاحظات مفصلة بعد الإرسال.",
            "load_exam": "تحميل امتحان",
            "available_from_generation": "يتوفر امتحان من صفحة الإنشاء.",
            "load_available": "تحميل الامتحان المتاح",
            "upload_file": "أو ارفع ملف امتحان (JSON, PDF, DOCX):",
            "upload_help": "ارفع ملف JSON أو PDF أو Word يحتوي على امتحان",
            "questions_title": "أسئلة الامتحان",
            "num_questions_label": "عدد الأسئلة:",
            "your_answer": "إجابتك:",
            "submit_exam": "إرسال الامتحان",
            "exam_completed": "تم الامتحان!",
            "score_final": "النتيجة النهائية",
            "feedback_per_question": "الملاحظات لكل سؤال",
            "your_response": "إجابتك:",
            "classification": "التصنيف:",
            "feedback": "الملاحظات:",
            "overall_feedback": "الملاحظات العامة",
            "download_results": "تحميل النتائج",
            "download_json": "JSON",
            "download_pdf": "PDF",
            "download_word": "Word",
            "new_exam": "امتحان جديد",
            "extracting_pdf": "استخراج النص من PDF...",
            "extracting_docx": "استخراج النص من مستند Word...",
            "analyzing": "تحليل الأسئلة...",
            "preview_text": "معاينة النص المستخرج (أول 500 حرف)",
            "success_json": "تم تحميل الامتحان بنجاح من ملف JSON!",
            "success_pdf": "سؤال(ات) مستخرجة من PDF!",
            "success_docx": "سؤال(ات) مستخرجة من مستند Word!",
            "error_invalid_format": "تنسيق امتحان غير صالح. يجب أن يحتوي الملف على قائمة 'questions'.",
            "error_no_questions": "لم يتم العثور على أسئلة. تحقق من تنسيق المستند.",
            "expected_format": "التنسيق المتوقع: 'Question N\\nCourse: ... | Difficulty: ...\\nنص السؤال...'",
        },
        # Common
        "common": {
            "difficulty_easy": "سهل",
            "difficulty_intermediate": "متوسط",
            "difficulty_hard": "صعب",
            "loading": "جارٍ التحميل...",
            "error": "خطأ",
            "success": "نجاح",
            "warning": "تحذير",
            "info": "معلومات",
        }
    }
}


def get_translation(language: str, category: str, key: str, default: str = None) -> str:
    """
    Get translation for a specific key in a category for the given language.
    
    Args:
        language: Language code ("Français", "English", "العربية")
        category: Translation category ("exam_generation", "exam_taking", "common")
        key: Translation key
        default: Default value if translation not found
    
    Returns:
        Translated string or default value
    """
    if language not in TRANSLATIONS:
        language = "Français"  # Fallback to French
    
    if category not in TRANSLATIONS[language]:
        return default or key
    
    return TRANSLATIONS[language][category].get(key, default or key)


def get_translations(language: str, category: str) -> dict:
    """
    Get all translations for a category in the given language.
    
    Args:
        language: Language code ("Français", "English", "العربية")
        category: Translation category ("exam_generation", "exam_taking", "common")
    
    Returns:
        Dictionary of translations for the category
    """
    if language not in TRANSLATIONS:
        language = "Français"  # Fallback to French
    
    return TRANSLATIONS[language].get(category, {})

