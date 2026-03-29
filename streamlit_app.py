import streamlit as st
import json
from src.chains import gen_chain, eval_chain, ped_chain
st.set_page_config(page_title="Advanced Math Exam Agent")
st.title("🧠 Advanced Math Exam Agent")

# Sidebar inputs
level = st.sidebar.selectbox("Class Level", ["9th Grade", "10th Grade", "11th Grade", "12th Grade"])
topic = st.sidebar.selectbox("Topic", ["Algebra", "Geometry", "Trigonometry", "Calculus"])
num_q = st.sidebar.slider("Number of Questions", 1, 10, 5)

# Initialize session state
if "exam" not in st.session_state:
    st.session_state.exam = None
if "answers" not in st.session_state:
    st.session_state.answers = []
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "pedagogy" not in st.session_state:
    st.session_state.pedagogy = None

# Generate Exam
if st.sidebar.button("Generate Exam"):
    st.session_state.exam = gen_chain.invoke({
        "level": level,
        "topic": topic,
        "num_questions": num_q,
    })
    st.session_state.answers = ["" for _ in st.session_state.exam]
    st.session_state.feedback = None
    st.session_state.pedagogy = None

# Show Exam and collect answers
if st.session_state.exam:
    st.header("📋 Exam Questions")
    for i, q in enumerate(st.session_state.exam):
        st.markdown(f"**Q{i+1}:** {q['prompt']}")
        st.session_state.answers[i] = st.text_input(f"Answer {i+1}", key=f"ans_{i}")

    if st.button("Submit Answers"):
        st.session_state.feedback = eval_chain.invoke({
            "exam_json": st.session_state.exam,
            "student_answers": st.session_state.answers,
        })
        st.session_state.pedagogy = None

# Display feedback and pedagogical summary
if st.session_state.feedback:
    st.header("📝 Feedback")
    for item in st.session_state.feedback:
        status = "✅ Correct" if item.get("correct") else "❌ Incorrect"
        st.markdown(f"- **{item['question']}**: {status}")
        st.write(f"_{item.get('comments', '').strip()}_")

    if st.button("Show Pedagogical Summary"):
        st.session_state.pedagogy = ped_chain.invoke({
            "feedback_json": st.session_state.feedback,
        })

if st.session_state.pedagogy:
    st.header("📚 Pedagogical Summary")
    st.write(st.session_state.pedagogy)

# Adaptive exam: harder if all correct
if st.session_state.feedback and all(item.get("correct") for item in st.session_state.feedback):
    if st.sidebar.button("Generate Harder Exam"):
        harder_level = f"{level} (Harder)"
        st.session_state.exam = gen_chain.invoke({
            "level": harder_level,
            "topic": topic,
            "num_questions": num_q,
        })
        st.session_state.answers = ["" for _ in st.session_state.exam]
        st.session_state.feedback = None
        st.session_state.pedagogy = None