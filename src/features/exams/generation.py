"""
Exam generation utilities (LLM-backed with fallbacks).
"""
from typing import List, Dict


def is_question_similar(new_question: str, existing_questions: List[str], threshold: float = 0.7) -> bool:
    """
    Check if a new question is too similar to existing ones.
    Uses simple word-based similarity to avoid duplicates.
    """
    if not existing_questions:
        return False
    
    new_words = set(new_question.lower().split())
    
    for existing_q in existing_questions:
        existing_words = set(existing_q.lower().split())
        
        # Calculate Jaccard similarity
        if len(new_words) == 0 or len(existing_words) == 0:
            continue
            
        intersection = len(new_words & existing_words)
        union = len(new_words | existing_words)
        similarity = intersection / union if union > 0 else 0
        
        if similarity > threshold:
            return True
    
    return False


def generate_exam_items(
    llm_manager_factory,
    grade_label: str,
    courses: List[str],
    difficulty_label: str,
    n: int,
    want_answers: bool,
    max_tokens_q: int = 500,
    max_tokens_a: int = 4000,
    course_percentages: dict = None,
) -> List[Dict]:
    try:
        llm_manager = llm_manager_factory()
        items: List[Dict] = []
        generated_questions: List[str] = []  # Track generated questions for uniqueness
        import random
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # Calculate number of questions per course based on percentages
        if course_percentages and len(course_percentages) > 1:
            course_counts = {}
            for course, percentage in course_percentages.items():
                course_counts[course] = max(1, int((percentage / 100) * n))
            
            # Adjust to match total
            total_questions = sum(course_counts.values())
            if total_questions != n:
                # Adjust the largest course
                largest_course = max(course_counts, key=course_counts.get)
                course_counts[largest_course] += (n - total_questions)
            
            # Create course list based on counts - GROUPED by course (not shuffled)
            course_cycle = []
            for course, count in sorted(course_counts.items(), key=lambda x: x[1], reverse=True):
                # Sort by count (descending) so larger courses come first
                course_cycle.extend([course] * count)
            # Don't shuffle - keep questions grouped by course
        else:
            # Default behavior - equal distribution, GROUPED by course
            questions_per_course = n // max(1, len(courses))
            remainder = n % max(1, len(courses))
            
            course_cycle = []
            for i, course in enumerate(courses):
                count = questions_per_course + (1 if i < remainder else 0)
                course_cycle.extend([course] * count)
            # Don't shuffle - keep questions grouped by course

        # Generate questions - they are now automatically grouped by course
        # Example: If 5 questions with 3 Fractions and 2 Geometry:
        #   Q1-Q3: Fractions, Q4-Q5: Geometry (grouped together)
        for i in range(n):
            course_name = course_cycle[i] if course_cycle else (courses[0] if courses else "Mathématiques")
            
            # Generate question with retry for uniqueness
            max_retries = 3
            question_text = ""
            
            for retry in range(max_retries):
                # Build context with previously generated questions to avoid duplication
                # For same-course questions, show only questions from the SAME course
                context_hint = ""
                if generated_questions:
                    # Filter to show only questions from the same course (for better variety within course)
                    same_course_questions = [q for j, q in enumerate(generated_questions) 
                                            if j < len(items) and items[j].get("course") == course_name]
                    
                    if same_course_questions:
                        context_hint = f"\n\nQuestions de {course_name} déjà générées (ÉVITE de créer des questions similaires):\n"
                        # Show last 3 questions from same course
                        for prev_q in same_course_questions[-3:]:
                            context_hint += f"- {prev_q[:100]}...\n"
                    else:
                        context_hint = f"\n\nPremière question de {course_name} - Sois créatif et original!\n"
                
                # Increase temperature slightly on retries for more variety
                temp = 0.2 + (retry * 0.2)
                
                prompt = (
                    "Tu es un professeur de mathématiques. Crée une question d'examen ORIGINALE et UNIQUE.\n"
                    f"Niveau: {grade_label}. Cours: {course_name}. Difficulté: {difficulty_label}.\n"
                    "RÈGLES STRICTES:\n"
                    "- La question doit être DIFFÉRENTE de toutes les questions précédentes\n"
                    "- Utilise des contextes variés (situations réelles différentes)\n"
                    "- Varie les valeurs numériques et les objets/personnages\n"
                    "- Évite absolument les répétitions\n"
                    "\n"
                    "FORMAT MATHÉMATIQUE (MARKDOWN UNIQUEMENT):\n"
                    "- Utiliser UNIQUEMENT le format Markdown - JAMAIS de LaTeX\n"
                    "- Pour math inline: $x + 2 = 5$ (simple dollar)\n"
                    "- Pour équations: $$x^2 + 3x - 2 = 0$$ (double dollar)\n"
                    "- Écrire les formules en texte simple quand possible\n"
                    "- Éviter toutes les commandes LaTeX comme \\text, \\dfrac, \\frac, \\mid, \\cap, \\cup, etc.\n"
                    "- Préférer des expressions simples comme P(A|B) = P(A et B) / P(B)\n"
                    f"{context_hint}\n"
                    "Fournis UNIQUEMENT l'énoncé de la nouvelle question."
                )
                
                tmpl = PromptTemplate(input_variables=[], template=prompt)
                chain = tmpl | llm_manager.create_llm_with_params(temperature=temp, max_tokens=max_tokens_q) | StrOutputParser()
                question_text = llm_manager.invoke_with_retry(chain, {})
                
                # Check if question is unique
                if not is_question_similar(question_text, generated_questions, threshold=0.6):
                    break  # Question is unique, use it
                # Otherwise retry with higher temperature
            
            # Add to generated questions list
            generated_questions.append(question_text)

            answer_text = ""
            if want_answers:
                aprompt = (
                    "Donne une solution claire et concise pour la question suivante.\n"
                    f"Question: {question_text}\n"
                    "INSTRUCTIONS:\n"
                    "- Donne une réponse directe et claire\n"
                    "- Inclus les étapes principales de calcul\n"
                    "- Sois concis mais complet\n"
                    "- Évite les explications trop détaillées\n"
                    "\n"
                    "FORMAT MATHÉMATIQUE (MARKDOWN UNIQUEMENT):\n"
                    "- Utiliser UNIQUEMENT le format Markdown - JAMAIS de LaTeX\n"
                    "- Pour math inline: $x + 2 = 5$ (simple dollar)\n"
                    "- Pour équations: $$x^2 + 3x - 2 = 0$$ (double dollar)\n"
                    "- Écrire les formules en texte simple quand possible\n"
                    "- Éviter toutes les commandes LaTeX comme \\text, \\dfrac, \\frac, \\mid, \\cap, \\cup, etc.\n"
                    "- Préférer des expressions simples comme P(A|B) = P(A et B) / P(B)\n"
                    "- Préférer (a + b) / 2 au lieu d'une fraction LaTeX\n"
                    "Format: Solution directe avec les étapes essentielles."
                )
                atmpl = PromptTemplate(input_variables=[], template=aprompt)
                achain = atmpl | llm_manager.create_llm_with_params(temperature=0.2, max_tokens=max_tokens_a) | StrOutputParser()
                answer_text = llm_manager.invoke_with_retry(achain, {})

            items.append(
                {
                    "question": (question_text or "").strip(),
                    "answer": (answer_text or "").strip(),
                    "course": course_name,
                    "difficulty": difficulty_label,
                }
            )
        return items
    except Exception:
        # Fallback simple generation
        items: List[Dict] = []
        for i in range(n):
            course_name = courses[i % max(1, len(courses))] if courses else "Mathématiques"
            q = f"[{grade_label}] ({difficulty_label}) {course_name} — Énoncez et résolvez le problème #{i+1}."
            a = "Solution simulée: montrer les étapes et conclure."
            items.append({
                "question": q,
                "answer": a if want_answers else "",
                "course": course_name,
                "difficulty": difficulty_label,
            })
        return items


