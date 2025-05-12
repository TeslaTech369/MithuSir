import streamlit as st
import json
from datetime import datetime

# Load JSON data
with open("data/result.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Page Config
st.set_page_config(page_title="🎓 Result Viewer", layout="centered")

# Background Gradient
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #e0f7fa, #f9fbe7);
    }
    .result-card {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        margin-top: 30px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        font-family: 'Segoe UI', sans-serif;
        color: #212121;
    }
    .result-card h2 {
        color: #388e3c;
        text-align: center;
        margin-bottom: 20px;
    }
    .info-row {
        font-size: 18px;
        margin: 8px 0;
    }
    .info-row span {
        font-weight: bold;
        color: #212121;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align:center; color:#1b5e20;'>📋 পরীক্ষার ফলাফল দেখুন</h1>", unsafe_allow_html=True)

# Input field
roll = st.text_input("🔍 রোল নম্বর দিন")

# Button
if st.button("📥 ফলাফল দেখুন"):
    student = next((s for s in results if s["roll"] == roll), None)

    if student:

        # Show result card
        st.markdown(f"""
        <div class='result-card'>
            <h2>📊 ফলাফল সংক্ষিপ্ত বিবরণ</h2>
            <div class='info-row'>👤 <span>নাম:</span> {student['name']}</div>
            <div class='info-row'>🎓 <span>রোল নম্বর:</span> {student['roll']}</div>
            <div class='info-row'>🧪 <span>পরীক্ষা:</span> {student['exam']}</div>
            <div class='info-row'>✅ <span>স্কোর:</span> <span style='color:green; font-weight:bold;'>{student['score']} নম্বর</span></div>
            <div class='info-row'>✔️ <span>সঠিক উত্তর:</span> {student['correct']} টি</div>
            <div class='info-row'>❌ <span>ভুল উত্তর:</span> {student['wrong']} টি</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❗ এই রোল নম্বরের জন্য কোনো ফলাফল পাওয়া যায়নি।")
