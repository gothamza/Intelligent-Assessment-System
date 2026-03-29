"""
Extraction and cleaning utilities for exam questions.
"""
from typing import List, Dict


def clean_mathematical_notation(text: str) -> str:
    """Clean and fix mathematical notation in question text."""
    import re
    text = re.sub(r"\[\[([^\]]+)\]", r"∫[\1", text)
    text = re.sub(r"\[\[", "∫", text)
    text = text.replace("π", "π").replace("√", "√").replace("∞", "∞")
    text = re.sub(r"(\d+)/(\d+)", r"\1/\2", text)
    text = re.sub(r"\^(\d+)", r"^\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_question_content(text: str) -> str:
    """Remove formatting lines and unwanted elements from raw text."""
    import re
    text = re.sub(r"^[_\-\s]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"Réponse:.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"Answer:.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n\s*\n", "\n", text)
    lines = text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    text = "\n".join(cleaned_lines)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_questions_simple(file_content: str, grade: str, difficulty: str) -> List[Dict]:
    """Fallback rule-based extraction of questions from text."""
    cleaned_content = clean_question_content(file_content)
    
    # Try to split by common question patterns
    import re
    
    # Split by question patterns
    question_patterns = [
        r'(?i)(?:question|q|exercice|problème|exercise|problem)\s*\d*[\.\)\-\:]',
        r'(?i)(?:question|q|exercice|problème|exercise|problem)\s*\d+',
        r'\n\s*\d+[\.\)\-\:]\s*',  # Numbered items
        r'\n\s*[a-zA-Z][\.\)\-\:]\s*',  # Lettered items
    ]
    
    # Try each pattern to split the content
    questions_text = []
    for pattern in question_patterns:
        parts = re.split(pattern, cleaned_content)
        if len(parts) > 1:
            questions_text = [part.strip() for part in parts if part.strip()]
            break
    
    # If no pattern worked, try to split by double newlines
    if not questions_text:
        questions_text = [part.strip() for part in cleaned_content.split('\n\n') if part.strip()]
    
    # If still no luck, split by single newlines and group
    if not questions_text or len(questions_text) == 1:
        lines = cleaned_content.split('\n')
        questions_text = []
        current_question = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_question.strip():
                    questions_text.append(current_question.strip())
                    current_question = ""
                continue
            
            # Check if this looks like a new question
            if (line.lower().startswith(('question', 'q', 'exercice', 'problème')) or
                (len(line) < 50 and any(char.isdigit() for char in line[:10]))):
                if current_question.strip():
                    questions_text.append(current_question.strip())
                current_question = line + " "
            else:
                current_question += line + " "
        
        if current_question.strip():
            questions_text.append(current_question.strip())
    
    # Convert to question objects
    questions: List[Dict] = []
    for i, question_text in enumerate(questions_text):
        if len(question_text.strip()) > 20:  # Only include substantial questions
            questions.append({
                "question_number": i + 1,
                "question": clean_mathematical_notation(question_text.strip()),
                "course": "Mathématiques",
                "difficulty": difficulty,
                "grade": grade,
            })
    
    return questions


def extract_questions_with_llm(file_content: str, grade: str, difficulty: str, create_llm_manager):
    """LLM-powered extraction. `create_llm_manager` is a callable returning llm_manager."""
    try:
        llm_manager = create_llm_manager()
        cleaned_content = clean_question_content(file_content)

        extraction_prompt = f"""
Tu es un expert en analyse de documents éducatifs. Analyse le contenu d'examen suivant et extrais TOUTES les questions de mathématiques.

CONTENU À ANALYSER:
{cleaned_content[:4000]}

INSTRUCTIONS CRITIQUES:
1. Identifie TOUTES les questions/exercices/problèmes de mathématiques dans le document
2. Sépare chaque question individuellement - ne les regroupe pas
3. Pour chaque question, extrais UNIQUEMENT le texte de la question (sans les lignes de formatage)
4. IGNORE les lignes avec des underscores (____), "Réponse:", "Answer:", et les lignes vides
5. Détermine le niveau de difficulté (Facile, Intermédiaire, Difficile) pour chaque question
6. Identifie le cours/thème mathématique concerné pour chaque question
7. Numérote les questions séquentiellement (1, 2, 3, etc.)
8. Chaque question doit être dans un objet séparé dans le tableau

FORMAT DE RÉPONSE (JSON strict):
{{
  "questions": [
    {{"question_number": 1, "question": "Texte de la première question...", "course": "Algèbre", "difficulty": "Facile", "grade": "{grade}"}},
    {{"question_number": 2, "question": "Texte de la deuxième question...", "course": "Géométrie", "difficulty": "Intermédiaire", "grade": "{grade}"}},
    {{"question_number": 3, "question": "Texte de la troisième question...", "course": "Calcul", "difficulty": "Difficile", "grade": "{grade}"}}
  ]
}}

RÈGLES IMPORTANTES:
- Chaque question doit être un objet séparé
- Nettoyez la notation mathématique (ex: [[a,b] -> ∫[a,b])
- Utilisez ∫, π, √, etc. pour les symboles mathématiques
- Répondez UNIQUEMENT en JSON valide
- Extrayez TOUTES les questions, pas seulement une partie
"""

        response = llm_manager.create_llm_with_params(temperature=0.1, max_tokens=2000).invoke(extraction_prompt)

        import json

        try:
            # Extract content from response
            response_content = getattr(response, "content", str(response))
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response_content
            
            result = json.loads(json_str)
            questions = result.get("questions", [])
            
            # If no questions found, try fallback
            if not questions:
                return extract_questions_simple(file_content, grade, difficulty)
            
            cleaned_questions: List[Dict] = []
            for q in questions:
                if q.get("question") and len(q["question"].strip()) > 10:
                    cleaned_question = clean_mathematical_notation(clean_question_content(q["question"].strip()))
                    if len(cleaned_question) < 20:
                        continue
                    cleaned_questions.append(
                        {
                            "question_number": q.get("question_number", len(cleaned_questions) + 1),
                            "question": cleaned_question,
                            "course": q.get("course", "Mathématiques"),
                            "difficulty": q.get("difficulty", difficulty),
                            "grade": q.get("grade", grade),
                        }
                    )
            
            # If we got questions, return them; otherwise fallback
            if cleaned_questions:
                return cleaned_questions
            else:
                return extract_questions_simple(file_content, grade, difficulty)
                
        except Exception as e:
            # If LLM extraction fails, use simple extraction
            return extract_questions_simple(file_content, grade, difficulty)
    except Exception:
        return extract_questions_simple(file_content, grade, difficulty)


