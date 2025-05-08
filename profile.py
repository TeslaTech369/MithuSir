import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_database"]

def profile_view():
    st.title("👤 My Profile")

    student_data = st.session_state.get("student")
    if not student_data:
        st.warning("Please log in as a student to view your profile.")
        return

    roll = student_data.get("roll")
    student = db.students.find_one({"roll": roll})

    if not student:
        st.error("Student record not found.")
        return

    # --- Profile Info ---
    st.markdown("## 📄 Personal Info")
    profile_url = student.get("profile", "https://i.postimg.cc/1tbKGHGw/251472878-211903867723008-3540371011058940641-n.jpg")
    try:
        img = Image.open(BytesIO(requests.get(profile_url).content))
        st.image(img, width=70, caption="Profile Picture")
    except:
        st.warning("⚠️ Could not load profile picture.")

    with st.form("update_profile"):
        st.text_input("Name", value=student.get("name", ""), disabled=True)
        st.text_input("Roll", value=student.get("roll", ""), disabled=True)
        class_val = st.text_input("Class", value=student.get("class", ""))
        section = st.text_input("Section", value=student.get("section", ""))
        institute = st.text_input("Institute", value=student.get("institute", ""))
        profile_link = st.text_input("Profile Picture URL", value=student.get("profile", ""))
        if st.form_submit_button("Update Profile"):
            db.students.update_one(
                {"roll": roll},
                {"$set": {
                    "class": class_val,
                    "section": section,
                    "institute": institute,
                    "profile": profile_link
                }}
            )
            st.success("✅ Profile updated. Please refresh.")
            st.rerun()

    # --- Exam History ---
    st.markdown("## 📝 Exam History")

    results = list(db.results.find({"roll": roll}).sort("timestamp", -1))
    if not results:
        st.info("No exam data available.")
        return

    data = [{
        "Exam": r.get("exam"),
        "Score": r.get("score"),
        "Total": r.get("total"),
        "Correct": r.get("correct", 0),
        "Wrong": r.get("wrong", 0),
        "Date": r.get("timestamp").strftime("%Y-%m-%d")
    } for r in results]

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # --- Graph Section ---
    st.markdown("## 📊 Performance Over Time")

    chart_df = df.copy()
    chart_df["Date"] = pd.to_datetime(chart_df["Date"])
    chart_df = chart_df.sort_values("Date")

    st.line_chart(data=chart_df.set_index("Date")[["Score"]], use_container_width=True)
