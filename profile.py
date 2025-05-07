import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_database"]

def profile_view():
    st.title("📊 Student Profile")

    if "roll" not in st.session_state:
        st.warning("Please enter your roll number in the Student tab first.")
        return

    roll = st.session_state["roll"]
    student = db.students.find_one({"roll": roll})
    if not student:
        st.error("Student not found.")
        return

    st.subheader(f"👤 Name: {student['name']}")
    st.markdown(f"**🎓 Roll Number:** {roll}")

    results = list(db.results.find({"roll": roll}))
    if not results:
        st.info("No exam records found.")
        return

    st.subheader("📈 Performance Overview")

    exam_names = [r["exam"] for r in results]
    scores = [r["score"] for r in results]
    totals = [r["total"] for r in results]

    # Calculate average and percentage
    average_score = round(sum(scores) / len(scores), 2)
    total_marks = sum(totals)
    percentage = round(sum(scores) * 100 / total_marks, 2) if total_marks > 0 else 0

    st.markdown(f"**📊 Average Score:** {average_score}")
    st.markdown(f"**📌 Overall Percentage:** {percentage}%")

    # Plot performance graph
    fig, ax = plt.subplots()
    ax.plot(exam_names, scores, marker='o', label="Score")
    ax.plot(exam_names, totals, linestyle='--', label="Total")
    ax.set_ylabel("Marks")
    ax.set_xlabel("Exam")
    ax.set_title("Exam Scores")
    ax.legend()
    st.pyplot(fig)

    # Detailed Results
    st.subheader("📃 Exam History")
    for r in results:
        st.markdown(f"""
        **📝 Exam:** {r['exam']}  
        **✅ Score:** {r['score']} / {r['total']}  
        **✔️ Correct:** {r['correct']}, ❌ Wrong: {r['wrong']}  
        **🕒 Date:** {r['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}
        ---
        """)
