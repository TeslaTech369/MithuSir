import streamlit as st
from pymongo import MongoClient
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import os

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_database"]

def profile_view():
    st.title("👤 Student Profile")

    # Check if student is logged in
    student_data = st.session_state.get("student")
    if not student_data:
        st.warning("Please log in as a student to view your profile.")
        return

    roll = student_data["roll"]
    student = db.students.find_one({"roll": roll})

    if not student:
        st.error("Student data not found.")
        return

    # --- Header Info ---
    st.markdown("### 🧾 Personal Information")

    # Handle Profile Picture
    profile_url = student.get("profile", "https://default-profile-url.com")
    try:
        response = requests.get(profile_url)
        img = Image.open(BytesIO(response.content))
        st.image(img, width=50)
    except Exception as e:
        st.warning(f"⚠️ Could not load profile picture. Error: {e}")

    # Display student info
    st.markdown(f"""
    **Name:** {student.get("name", "")}  
    **Roll:** {student.get("roll", "")}  
    """)

    # --- Editable Info ---
    st.markdown("### ✏️ Edit Info")
    with st.form("update_profile"):
        st.text_input("Name", value=student.get("name", ""), disabled=True)
        st.text_input("Roll", value=student.get("roll", ""), disabled=True)
        class_val = st.text_input("Class", value=student.get("class", ""))
        section = st.text_input("Section", value=student.get("section", ""))
        institute = st.text_input("Institute", value=student.get("institute", ""))
        new_profile_url = st.text_input("Profile Picture URL", value=student.get("profile", ""))

        submitted = st.form_submit_button("Update Info")
        if submitted:
            db.students.update_one(
                {"roll": roll},
                {"$set": {
                    "class": class_val,
                    "section": section,
                    "institute": institute,
                    "profile": new_profile_url
                }}
            )
            st.success("✅ Profile updated successfully!")
            st.rerun()

    # --- Exam History ---
    st.markdown("### 📚 Exam History")

    results = list(db.results.find({"roll": roll}).sort("timestamp", -1))
    if not results:
        st.info("No exam records found.")
        return

    data = []
    for r in results:
        data.append({
            "Exam": r["exam"],
            "Score": f"{r['score']} / {r['total']}",
            "Correct": r.get("correct", "N/A"),
            "Wrong": r.get("wrong", "N/A"),
            "Date": r["timestamp"].strftime("%Y-%m-%d")
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # --- Performance Chart ---
    st.markdown("### 📈 Performance Over Time")

    chart_data = pd.DataFrame({
        "Date": [r["timestamp"].strftime("%Y-%m-%d") for r in results][::-1],
        "Score": [r["score"] for r in results][::-1],
    })

    st.line_chart(chart_data.set_index("Date"))
