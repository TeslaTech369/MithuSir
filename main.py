import streamlit as st
from pymongo import MongoClient
from admin import admin_login, admin_panel
from student import student_interface, exam_interface, solve_sheet_view
from dotenv import load_dotenv
import os

st.set_page_config(page_title="MMC", page_icon="📝")

# Load logo image
logo_url = "https://i.postimg.cc/x1nPTRSC/MMC.jpg"

st.markdown(f"""
    <style>
        .header-container {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .circular-image {{
            width: 65px;
            height: 65px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #f0eded;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .app-title {{
            font-size: 32px;
            font-weight: bold;
            color: #f0eded;
        }}
    </style>
    <div class="header-container">
        <img src="{logo_url}" class="circular-image">
        <div class="app-title">MMC</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar menu
menu = ["Student", "Admin", "Solve Sheet"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Admin":
    if st.session_state.get("admin_logged_in"):
        admin_panel()
    else:
        admin_login()
elif choice == "Student":
    if "student" in st.session_state:
        exam_interface()
    else:
        student_interface()
elif choice == "Solve Sheet":
    solve_sheet_view()
