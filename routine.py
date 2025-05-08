import streamlit as st
import json
import os

def load_routine():
    path = os.path.join("data", "routine.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def routine_view():
    st.title("📅 Class Routine")

    routine_data = load_routine()

    st.markdown("""
    <style>
        .routine-box {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .routine-title {
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .class-row {
            padding: 8px;
            background-color: #ffffff;
            border-radius: 5px;
            margin-bottom: 5px;
            border-left: 5px solid #3498db;
        }
    </style>
    """, unsafe_allow_html=True)

    for day in routine_data:
        st.markdown(f"""
        <div class="routine-box">
            <div class="routine-title">📆 {day['day']}</div>
        """, unsafe_allow_html=True)
        for cls in day["classes"]:
            st.markdown(f"""
                <div class="class-row">
                    ⏰ <b>{cls['time']}</b><br>
                    📚 <b>{cls['subject']}</b><br>
                    👨‍🏫 <i>{cls['teacher']}</i>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
