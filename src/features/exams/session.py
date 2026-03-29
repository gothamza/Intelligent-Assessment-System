"""
Exam session and timer utilities.
"""
from datetime import datetime
import streamlit as st


def format_time(seconds: int) -> str:
    """Format seconds into HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def start_exam_timer(duration_minutes: int = None) -> None:
    """Start the exam timer"""
    st.session_state.exam_start_time = datetime.now()
    if duration_minutes is not None and duration_minutes > 0:
        st.session_state.exam_duration = duration_minutes * 60  # Convert to seconds
        st.session_state.time_remaining = st.session_state.exam_duration
    else:
        # No time limit
        st.session_state.exam_duration = None
        st.session_state.time_remaining = None


def update_timer() -> None:
    """Update the remaining time"""
    if (hasattr(st.session_state, 'exam_start_time') and 
        st.session_state.exam_start_time and 
        hasattr(st.session_state, 'exam_duration') and 
        st.session_state.exam_duration is not None):
        
        elapsed = (datetime.now() - st.session_state.exam_start_time).total_seconds()
        st.session_state.time_remaining = max(0, st.session_state.exam_duration - elapsed)
        
        # Auto-submit if time is up
        if st.session_state.time_remaining <= 0 and not st.session_state.get('exam_completed', False):
            st.session_state.exam_completed = True
            st.rerun()


def get_exam_key_from_url() -> str:
    """Get exam key from URL parameters"""
    query_params = st.query_params
    return query_params.get("exam_key", "")


def initialize_exam_session() -> None:
    """Initialize exam session state variables"""
    if 'exam_session' not in st.session_state:
        st.session_state.exam_session = None
    if 'exam_start_time' not in st.session_state:
        st.session_state.exam_start_time = None
    if 'exam_duration' not in st.session_state:
        st.session_state.exam_duration = 0
    if 'student_answers' not in st.session_state:
        st.session_state.student_answers = {}
    if 'time_remaining' not in st.session_state:
        st.session_state.time_remaining = 0
    if 'exam_completed' not in st.session_state:
        st.session_state.exam_completed = False
