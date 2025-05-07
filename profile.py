import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_database"]

def profile_view():
    st.title("🎓 Student Profile")

    if "roll" not in st.session_state:
        st.warning("Please enter your roll number in the Student tab first.")
        return

    roll = st.session_state["roll"]
    student = db.students.find_one({"roll": roll})
    if not student:
        st.error("Student not found.")
        return

    # Default profile image
    profile_pic_url = student.get("photo", "https://i.postimg.cc/1tbKGHGw/251472878-211903867723008-3540371011058940641-n.jpg")

    # Profile header section
    st.markdown(f"""
        <style>
            .profile-container {{
                display: flex;
                align-items: center;
                gap: 20px;
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .profile-pic {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #999;
            }}
            .profile-info {{
                font-size: 16px;
            }}
        </style>
        <div class="profile-container">
            <img src="{profile_pic_url}" class="profile-pic">
            <div class="profile-info">
                <strong>Name:</strong> {student['name']}<br>
                <strong>Roll:</strong> {roll}<br>
                <strong>Class:</strong> {student.get('class', 'N/A')}<br>
                <strong>Section:</strong> {student.get('section', 'N/A')}<br>
                <strong>Institute:</strong> {student.get('institute', 'MMC Coaching')}<br>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Exam performance data
    results = list(db.results.find({"roll": roll}))
    if not results:
        st.info("No exam records found.")
        return

    st.subheader("📊 Performance Overview")

    exam_names = [r["exam"] for r in results]
    scores = [r["score"] for r in results]
    totals = [r["total"] for r in results]

    average_score = round(sum(scores) / len(scores), 2)
    total_marks = sum(totals)
    percentage = round(sum(scores) * 100 / total_marks, 2) if total_marks > 0 else 0

    st.markdown(f"**✅ Average Score:** {average_score}")
    st.markdown(f"**📈 Overall Percentage:** {percentage}%")
    st.markdown(f"**🧮 Exams Taken:** {len(results)}")

    # Score chart
    fig, ax = plt.subplots()
    ax.plot(exam_names, scores, marker='o', color='green', label="Score")
    ax.plot(exam_names, totals, linestyle='--', color='gray', label="Total")
    ax.set_ylabel("Marks")
    ax.set_xlabel("Exam")
    ax.set_title("Exam Scores Over Time")
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    st.pyplot(fig)

    # Detailed result list
    st.subheader("📃 Exam History")
    for r in results:
        st.markdown(f"""
        **📝 Exam:** {r['exam']}  
        **✅ Score:** {r['score']} / {r['total']}  
        **✔️ Correct:** {r.get('correct', 'N/A')}, ❌ Wrong: {r.get('wrong', 'N/A')}  
        **🕒 Date:** {r['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}
        ---
        """)

