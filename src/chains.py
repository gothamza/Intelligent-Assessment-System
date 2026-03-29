import os
import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

# Load environment
load_dotenv()

# Initialize LLM via OpenRouter
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat-v3-0324:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    # openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
)

# JSON parser
parser = JsonOutputParser()

# 1. Exam generation runnable
gen_prompt = PromptTemplate(
    input_variables=["level", "topic", "num_questions"],
    template="""
Generate {num_questions} {level}-level {topic} questions.
Output as a JSON list of objects with fields 'prompt' and 'answer'.
""",
)
gen_chain = gen_prompt | llm | parser

# 2. Evaluation runnable
eval_prompt = PromptTemplate(
    input_variables=["exam_json", "student_answers"],
    template="""
Given exam JSON: {exam_json} and student answers: {student_answers},
return a JSON list of objects with: question, correct (true/false), comments.
""",
)
eval_chain = eval_prompt | llm | parser

# 3. Pedagogical summary runnable
ped_prompt = PromptTemplate(
    input_variables=["feedback_json"],
    template="""
Based on feedback: {feedback_json}, provide a pedagogical summary
listing strengths, weaknesses, and study recommendations.
""",
)
ped_chain = ped_prompt | llm


import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_llm(temperature=0.3, max_tokens=500):
    """Initializes and returns the Language Model instance."""
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        openai_api_key=os.getenv("GROQ_API_KEY2"),
        temperature=temperature,
        max_tokens=max_tokens
    )

def create_feedback_chain(llm: ChatOpenAI):
    """Creates the chain for generating individual pedagogical feedback."""
    feedback_template = """
Tu es un professeur de mathématiques bienveillant, patient et encourageant.
Ton objectif est de fournir un feedback constructif à un élève qui a fait une erreur.
Ne donne PAS la réponse directe. Guide l'élève pour qu'il trouve la solution par lui-même.

**Question :**
{question}

**Réponse de l'élève :**
{reponse_eleve}

**Instructions pour le feedback :**
1. Commence par une phrase positive et encourageante.
2. Identifie l'erreur principale de l'élève de manière simple et claire.
3. Pose une question ou donne un indice pour l'aider à corriger son erreur.
4. Ton feedback doit être court, en 2 ou 3 phrases maximum.

**Feedback Pédagogique :**
"""
    feedback_prompt = PromptTemplate(
        input_variables=["question", "reponse_eleve"],
        template=feedback_template
    )
    return feedback_prompt | llm | StrOutputParser()

def create_global_summary_chain(llm: ChatOpenAI):
    """Creates the chain for generating a global summary and action plan."""
    global_feedback_template = """
Tu es un tuteur expert qui analyse une série de feedbacks pour créer un plan d'action personnalisé.

Voici la liste des feedbacks :
---
{individual_feedbacks}
---

**Ta mission :**
1.  Identifie 1 ou 2 concepts clés avec lesquels l'élève a des difficultés.
2.  Pour chaque concept, propose une mini-leçon, un exercice d'application, et sa solution détaillée.
3.  Termine avec un message d'encouragement.
4.  Structure ta réponse en Markdown.

**Plan d'Action Personnalisé :**
"""
    global_feedback_prompt = PromptTemplate(
        input_variables=["individual_feedbacks"],
        template=global_feedback_template
    )
    return global_feedback_prompt | llm | StrOutputParser()