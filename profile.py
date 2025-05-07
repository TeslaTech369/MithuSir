import matplotlib.pyplot as plt
import pandas as pd

def profile_view():
    if "roll" not in st.session_state:
        st.warning("Please enter your roll number first.")
        return

    roll = st.session_state["roll"]
    st.title("📊 Student Profile & Performance")

    results = list(db.results.find({"roll": roll}))

    if not results:
        st.info("You haven't taken any exams yet.")
        return

    st.subheader("📄 Your Exam History")

    for res in results:
        st.markdown(f"### 📝 {res['exam']}")
        st.write(f"✅ **Score:** {res['score']} / {res['total']}")
        st.write(f"✔️ Correct: {res['correct']} | ❌ Wrong: {res['wrong']}")
        st.write(f"🕒 Date: {res['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("---")

    # 📈 Plotting performance graph
    st.subheader("📈 Performance Over Time")

    df = pd.DataFrame(results)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig, ax = plt.subplots()
    ax.plot(df['timestamp'], df['score'], marker='o', linestyle='-')
    ax.set_title('Exam Scores Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Score')
    ax.grid(True)

    st.pyplot(fig)
