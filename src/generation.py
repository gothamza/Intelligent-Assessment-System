from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_feedback_chain(llm: ChatOpenAI):
    """
    Creates and returns a LangChain chain for generating pedagogical feedback.

    Args:
        llm: The language model to use for generation.

    Returns:
        A LangChain runnable instance.
    """
    feedback_template = """
Tu es un professeur de mathématiques bienveillant, patient et encourageant.
Ton objectif est de fournir un feedback constructif à un élève qui a fait une erreur.

Ne donne PAS la réponse directe. Guide l'élève pour qu'il trouve la solution par lui-même.

Voici la question et la réponse de l'élève :

**Question :**
{question}

**Réponse de l'élève :**
{reponse_eleve}

**Instructions pour le feedback :**
1.  Commence par une phrase positive et encourageante.
2.  Identifie l'erreur principale de l'élève de manière simple et claire.
3.  Pose une question ou donne un indice pour l'aider à corriger son erreur.
4.  Ton feedback doit être court, en 2 ou 3 phrases maximum.

**Feedback Pédagogique :**
"""

    feedback_prompt = PromptTemplate(
        input_variables=["question", "reponse_eleve"],
        template=feedback_template
    )

    parser = StrOutputParser()
    
    return feedback_prompt | llm | parser