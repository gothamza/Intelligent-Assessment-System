"""
Answer classification and feedback generation utilities.
"""
from typing import List, Tuple


def classify_answer(llm_manager, question: str, student_answer: str) -> str:
    """Classify student answer quality using LLM"""
    classification_prompt = f"""
    Tu es un expert en évaluation pédagogique de mathématiques. Évalue la qualité de cette réponse d'étudiant.

    QUESTION: {question}
    RÉPONSE DE L'ÉTUDIANT: {student_answer}

    CRITÈRES D'ÉVALUATION:
    
    "correcte" = La réponse est complètement juste, montre une compréhension parfaite, et inclut tous les éléments nécessaires.
    
    "partiellement_correcte" = La réponse montre une compréhension partielle avec:
    - Quelques bonnes idées mais des erreurs mineures
    - Approche correcte mais calculs partiellement faux
    - Réponse incomplète mais dans la bonne direction
    - Quelques éléments justes mélangés avec des erreurs
    - Méthode correcte mais résultat final incorrect
    
    "incorrecte" = La réponse est fondamentalement fausse, montre une mauvaise compréhension, ou est complètement à côté.

    EXEMPLES:
    - Si l'étudiant a la bonne méthode mais fait une erreur de calcul = "partiellement_correcte"
    - Si l'étudiant comprend partiellement le concept = "partiellement_correcte"  
    - Si l'étudiant donne des éléments corrects mais incomplets = "partiellement_correcte"
    - Si l'étudiant a une approche créative mais quelques erreurs = "partiellement_correcte"

    Réponds UNIQUEMENT par un de ces trois mots: correcte, partiellement_correcte, ou incorrecte.
    """
    
    classification = llm_manager.create_llm_with_params(temperature=0.1).invoke(classification_prompt)
    # Extract content from AIMessage if needed
    if hasattr(classification, 'content'):
        classification = classification.content
    
    # Clean and normalize the classification
    classification = str(classification).strip().lower()
    
    # Handle variations in LLM responses
    if "partiellement" in classification or "partiel" in classification:
        return "partiellement_correcte"
    elif "correct" in classification and "incorrect" not in classification:
        return "correcte"
    elif "incorrect" in classification or "faux" in classification or "erreur" in classification:
        return "incorrecte"
    else:
        # Default fallback based on common patterns
        if classification in ["correcte", "correct", "juste", "bonne"]:
            return "correcte"
        elif classification in ["partiellement_correcte", "partiel", "partiellement"]:
            return "partiellement_correcte"
        elif classification in ["incorrecte", "incorrect", "faux", "mauvaise"]:
            return "incorrecte"
        else:
            # If unclear, default to partially correct (more lenient)
            return "partiellement_correcte"


def generate_individual_feedback(llm_manager, question: str, student_answer: str, classification: str) -> str:
    """Generate individual feedback for a student answer"""
    feedback_prompt = f"""
    Donnez un feedback pédagogique constructif pour cette réponse d'étudiant.
    
    Question: {question}
    Réponse de l'étudiant: {student_answer}
    Classification: {classification}
    
    Donnez un feedback:
    - Constructif et encourageant
    - Spécifique à la réponse
    - Avec des suggestions d'amélioration si nécessaire
    - En français
    
    Maximum 200 mots.
    """
    
    feedback = llm_manager.create_llm_with_params(temperature=0.3).invoke(feedback_prompt)
    # Extract content from AIMessage if needed
    if hasattr(feedback, 'content'):
        feedback = feedback.content
    return str(feedback).strip()


def generate_overall_feedback(llm_manager, score: float, correct_count: int, partial_count: int, total_questions: int) -> str:
    """Generate overall exam feedback"""
    overall_feedback_prompt = f"""
    Donnez un feedback global pour cet examen de mathématiques.
    
    Score: {score:.1f}%
    Questions correctes: {correct_count}
    Questions partiellement correctes: {partial_count}
    Questions incorrectes: {total_questions - correct_count - partial_count}
    
    Donnez un feedback global:
    - Encourageant et constructif
    - Avec des conseils pour s'améliorer
    - En français
    - Maximum 300 mots
    """
    
    overall_feedback = llm_manager.create_llm_with_params(temperature=0.3).invoke(overall_feedback_prompt)
    # Extract content from AIMessage if needed
    if hasattr(overall_feedback, 'content'):
        overall_feedback = overall_feedback.content
    return str(overall_feedback).strip()


def process_exam_results(llm_manager, exam_questions: List[dict], student_answers: dict) -> Tuple[List[str], List[str], float, str]:
    """
    Process exam results: classify answers, generate feedback, calculate score, and create overall feedback.
    
    Returns:
        - classifications: List of classification results
        - individual_feedbacks: List of individual feedbacks
        - score: Overall score percentage
        - overall_feedback: Overall exam feedback
    """
    classifications = []
    individual_feedbacks = []
    
    for i, question in enumerate(exam_questions):
        student_answer = student_answers.get(str(i), "")
        if student_answer:
            # Classify answer
            classification = classify_answer(llm_manager, question['question'], student_answer)
            classifications.append(classification)
            
            # Generate individual feedback
            feedback = generate_individual_feedback(llm_manager, question['question'], student_answer, classification)
            individual_feedbacks.append(feedback)
    
    # Calculate score
    correct_count = classifications.count('correcte')
    partial_count = classifications.count('partiellement_correcte')
    total_questions = len(classifications)
    
    score = ((correct_count + partial_count * 0.5) / total_questions * 100) if total_questions > 0 else 0
    
    # Generate overall feedback
    overall_feedback = generate_overall_feedback(llm_manager, score, correct_count, partial_count, total_questions)
    
    return classifications, individual_feedbacks, score, overall_feedback
