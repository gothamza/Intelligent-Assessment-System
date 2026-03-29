"""
Shared UI components for the application.
"""
import streamlit as st
from typing import List, Dict, Any, Optional


def show_exam_header(exam_title: str, exam_info: str) -> None:
    """Display exam header with title and info"""
    st.markdown(f"## {exam_title}")
    st.markdown(f"**{exam_info}**")
    st.divider()


def show_timer_display(time_remaining: int) -> None:
    """Display countdown timer"""
    if time_remaining > 0:
        hours = time_remaining // 3600
        minutes = (time_remaining % 3600) // 60
        seconds = time_remaining % 60
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Heures", f"{hours:02d}")
        with col2:
            st.metric("Minutes", f"{minutes:02d}")
        with col3:
            st.metric("Secondes", f"{seconds:02d}")
    else:
        st.error("⏰ Temps écoulé!")


def show_question_card(question_num: int, question: Dict[str, Any], student_answer: str = "") -> str:
    """Display a question card and return the student's answer"""
    with st.container():
        st.markdown(f"### Question {question_num + 1}")
        
        # Question metadata
        if 'course' in question and 'difficulty' in question:
            st.markdown(f"**Cours:** {question['course']} | **Difficulté:** {question['difficulty']}")
        
        # Question text
        st.markdown(question['question'])
        
        # Answer input
        answer = st.text_area(
            f"Votre réponse (Question {question_num + 1})",
            value=student_answer,
            height=100,
            key=f"answer_{question_num}"
        )
        
        st.divider()
        return answer


def show_results_summary(score: float, correct_count: int, partial_count: int, total_questions: int) -> None:
    """Display exam results summary"""
    st.subheader("📊 Résumé des Résultats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Score Total", f"{score:.1f}%")
    
    with col2:
        st.metric("Correctes", correct_count)
    
    with col3:
        st.metric("Partielles", partial_count)
    
    with col4:
        st.metric("Incorrectes", total_questions - correct_count - partial_count)


def show_individual_feedback(question_num: int, question: str, student_answer: str, 
                           classification: str, feedback: str) -> None:
    """Display individual question feedback"""
    with st.expander(f"Question {question_num + 1} - {classification.title()}"):
        st.markdown(f"**Question:** {question}")
        st.markdown(f"**Votre réponse:** {student_answer}")
        
        # Classification badge
        if classification == "correcte":
            st.success(f"✅ {classification.title()}")
        elif classification == "partiellement_correcte":
            st.warning(f"⚠️ {classification.title()}")
        else:
            st.error(f"❌ {classification.title()}")
        
        st.markdown(f"**Feedback:** {feedback}")


def show_overall_feedback(feedback: str) -> None:
    """Display overall exam feedback"""
    st.subheader("💬 Feedback Global")
    st.info(feedback)


def show_loading_spinner(message: str = "Chargement..."):
    """Display loading spinner - returns a context manager"""
    return st.spinner(message)


def show_success_message(message: str) -> None:
    """Display success message"""
    st.success(f"✅ {message}")


def show_error_message(message: str) -> None:
    """Display error message"""
    st.error(f"❌ {message}")


def show_warning_message(message: str) -> None:
    """Display warning message"""
    st.warning(f"⚠️ {message}")


def show_info_message(message: str) -> None:
    """Display info message"""
    st.info(f"ℹ️ {message}")


def create_metric_card(title: str, value: str, delta: Optional[str] = None) -> None:
    """Create a metric card"""
    st.metric(title, value, delta)


def show_progress_bar(current: int, total: int, label: str = "Progression") -> None:
    """Show progress bar"""
    progress = current / total if total > 0 else 0
    st.progress(progress)
    st.caption(f"{label}: {current}/{total} ({progress:.1%})")


def show_data_table(data: List[Dict], title: str = "Données") -> None:
    """Display data in a table format"""
    if data:
        st.subheader(title)
        st.dataframe(data, use_container_width=True)
    else:
        st.info("Aucune donnée à afficher")
