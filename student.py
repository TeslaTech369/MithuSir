import streamlit as st
from pymongo import MongoClient
from PIL import Image
import io
from datetime import datetime
import os
import random
import base64

client = MongoClient(os.getenv("MONGO_URI"))
db = client["exam_database"]

def student_interface():
    st.title("🖥️Student Exam Portal")

    # Check if roll is already submitted
    if "roll_submitted" not in st.session_state:
        st.session_state["roll_submitted"] = False

    if not st.session_state["roll_submitted"]:
        roll = st.text_input("Enter Roll Number")
        if st.button("Submit Roll"):
            student = db.students.find_one({"roll": roll})
            if not student:
                st.warning("⚠️স্যারের থেকে রোল নিয়ে আসো আগে")
                noroll = "https://i.postimg.cc/jqDL7T3p/access.png"
                st.image(noroll, caption="noroll", use_container_width=True)
            else:
                st.session_state["roll"] = roll
                st.session_state["student_name"] = student["name"]
                st.session_state["roll_submitted"] = True
                st.rerun()
        return

    exams = list(db.exams.find())  # Query the exams collection
    if not exams:
        st.warning("⚠️No exams available.")
        return

    exam_options = [exam["name"] for exam in exams]
    selected_exam = st.selectbox("Select Exam", exam_options)

    # Check if the student already attempted this exam
    already_attempted = db.responses.find_one({
        "roll": st.session_state["roll"],
        "exam": selected_exam
    })

    if already_attempted:
        st.error(f"❌এইইইইইইইই,{st.session_state['student_name']} তুমি একবার পরীক্ষা দিছো না আবার কেনো???")
        chitting = "https://i.postimg.cc/BvJ0c5S8/cheating.png"
        st.image(chitting, caption="cheating", use_container_width=True)
        return

    if st.button("Start Exam"):
        questions = list(db.questions.find({"exam": selected_exam}))
        if not questions:
            st.warning("⚠️চিন্তা করো না কোশ্চেন চলে আসবে অপেক্ষা করো একটু")
            noqus = "https://i.postimg.cc/qMfM633K/no-question.png"
            st.image(noqus, caption="No Question", use_container_width=True)
            return

        random.shuffle(questions)
        duration = next(exam["duration"] for exam in exams if exam["name"] == selected_exam)

        # Initialize session state
        st.session_state["student"] = {"name": st.session_state["student_name"], "roll": st.session_state["roll"]}
        st.session_state["exam"] = selected_exam
        st.session_state["start_time"] = datetime.now()
        st.session_state["questions"] = questions
        st.session_state["responses"] = {}
        st.session_state["current_question"] = 0
        st.session_state["exam_duration"] = duration
        st.rerun()


# Function to convert image bytes to base64 for embedding in HTML
def image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode() if img_bytes else ""


# Exam interface function
def exam_interface():
    elapsed_time = (datetime.now() - st.session_state["start_time"]).seconds
    remaining_time = st.session_state["exam_duration"] * 60 - elapsed_time

    if remaining_time <= 0:
        st.warning("🕒Time's up! Submitting exam...")
        submit_exam()
        return

    minutes, seconds = divmod(remaining_time, 60)
    st.info(f"⏳Time Remaining: {minutes} minutes {seconds} seconds")

    questions = st.session_state["questions"]
    for idx, q in enumerate(questions):
        st.markdown(f"### Question {idx + 1}")
        st.write(q["question"])

        # Display question image if exists
        if q.get("image"):
            st.image(Image.open(io.BytesIO(q["image"])), caption="Question Image")

        options = q["options"]
        option_images = q.get("option_images", [None] * len(options))

        # Generate unique key for each question's answer
        answer_key = f"answer_q_{idx}"

        # Track selected option
        if "selected_option" not in st.session_state:
            st.session_state["selected_option"] = None

        # Build list of rendered options with image previews
        rendered_options = []
        for i, option in enumerate(options):
            image_html = ""
            if option_images[i]:
                img_b64 = image_to_base64(option_images[i])
                image_html = f'<img src="data:image/png;base64,{img_b64}" style="max-width:120px; max-height:100px; margin-top:5px;" />'

            option_block = f"""
                <div style="border: 2px solid #ccc; border-radius: 12px; padding: 12px; margin-bottom: 10px; cursor: pointer;">
                    <strong>{option}</strong>
                    {image_html}
                </div>
            """
            rendered_options.append(option_block)

        # Create radio buttons for each option and select the corresponding card
        selected = st.radio(
            f"Select the answer for Question {idx + 1}",
            options,
            index=None,  # Set the default selected option to None
            key=f"question_{idx}",  # Unique key per question
            horizontal=False,
        )

        # Now show the visual cards just below, highlighting the selected one
        for i, option_html in enumerate(rendered_options):
            option_value = options[i]
            is_selected = (selected == option_value)
            highlight = "3px solid #4CAF50" if is_selected else "1px solid #ccc"
            bg = "#e8f5e9" if is_selected else "#fff"

            # Render the option card with style
            st.markdown(
                f"""
                <div style="border: {highlight}; background-color: {bg}; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                    {option_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Save selected option
        st.session_state["responses"][q["question"]] = selected

    if st.button("✔️Submit Exam"):
        submit_exam()


def submit_exam():
    responses = st.session_state["responses"]
    questions = st.session_state["questions"]
    exam_info = db.exams.find_one({"name": st.session_state["exam"]})
    negative_marking = exam_info.get("negative_marking", False)

    correct = 0
    wrong = 0
    score = 0

    for q in questions:
        user_answer = responses.get(q["question"])
        if user_answer is None:
            continue
        elif user_answer == q["answer"]:
            correct += 1
        else:
            wrong += 1

    if negative_marking:
        score = max(correct - 0.25 * wrong, 0)
    else:
        score = correct

    total = len(questions)
    result = {
        "name": st.session_state["student"]["name"],
        "roll": st.session_state["student"]["roll"],
        "exam": st.session_state["exam"],
        "responses": responses,
        "score": score,
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "timestamp": datetime.now()
    }
    db.results.insert_one(result)

    # Save responses in the database to track attempts
    db.responses.insert_one({
        "roll": st.session_state["student"]["roll"],
        "exam": st.session_state["exam"],
        "responses": responses,
        "submitted_at": datetime.now()
    })

    st.success(f"✔️Exam Completed! Your Score: {score}/{total} (Correct: {correct}, Wrong: {wrong})")

    st.subheader("Your Exam Results:")
    for idx, q in enumerate(questions):
        st.markdown(f"### Question {idx + 1}")
        st.write(q["question"])
        for i, option in enumerate(q["options"], 1):
            st.write(f"{i}. {option}")
        student_answer = responses.get(q["question"], "No Answer")
        if student_answer == q["answer"]:
            st.success(f"**Your Answer:** {student_answer} - Correct!")
        elif student_answer == "No Answer":
            st.warning(f"**Your Answer:** {student_answer} - Not Attempted")
        else:
            st.warning(f"**Your Answer:** {student_answer} - Incorrect!")
        st.success(f"**Correct Answer:** {q['answer']}")
        st.write("---")

    # Remove session state variables
    for key in ["student", "exam", "start_time", "questions", "responses", "exam_duration"]:
        st.session_state.pop(key, None)


def solve_sheet_view():
    st.title("📐Solve Sheets")

    pdfs = list(db.solve_sheets.find().sort("uploaded_at", -1))
    if not pdfs:
        st.info("❌কিচ্ছু নাই")
        nopdff = "https://i.postimg.cc/VkWVB3Hw/nothing.png"
        st.image(nopdff, caption="No pdf", use_container_width=True)
        return

    for pdf in pdfs:
        st.markdown(f"### 📄 {pdf.get('name', 'Untitled')}")

        if 'pdf_link' in pdf:
            st.markdown(f"[🔗Open in New Tab]({pdf['pdf_link']})", unsafe_allow_html=True)
            st.components.v1.iframe(pdf['pdf_link'], height=600, scrolling=True)
        else:
            st.warning("⚠️কোনো কাজের না এই লিংক")
            useless = "https://i.postimg.cc/c4V9SdP0/useless.png"
            st.image(useless, caption="Useless", use_container_width=True)
        st.markdown("---")
