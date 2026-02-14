# ==========================================
# AI Sports Athlete Management System
# Enhanced Evaluation Version (Stable)
# ==========================================

import streamlit as st
import cv2
import mediapipe as mp
import sqlite3
import pandas as pd
from datetime import datetime

# -------------------------
# Database Setup
# -------------------------
conn = sqlite3.connect("athletes.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS results(
    name TEXT,
    age INT,
    reps INT,
    grade TEXT,
    date TEXT
)
""")
conn.commit()

# -------------------------
# Helper Functions
# -------------------------
def save_result(name, age, reps, grade):
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)",
              (name, age, reps, grade, str(datetime.now())))
    conn.commit()

def calculate_ai_score(age, reps):

    if age <= 12:
        expected = 15
    elif age <= 18:
        expected = 25
    else:
        expected = 20

    percentage = (reps / expected) * 100

    if percentage >= 120:
        grade = "Elite"
    elif percentage >= 90:
        grade = "Strong"
    elif percentage >= 60:
        grade = "Average"
    else:
        grade = "Beginner"

    ai_score = min(int(percentage), 150)

    return ai_score, grade

# -------------------------
# MediaPipe Setup
# -------------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# -------------------------
# Sit-up Counter (UNCHANGED)
# -------------------------
def count_situps():

    cap = cv2.VideoCapture(0)

    counter = 0
    stage = None

    print("Press Q to stop the test.")

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            shoulder_y = lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y
            hip_y = lm[mp_pose.PoseLandmark.LEFT_HIP].y

            diff = hip_y - shoulder_y

            if diff > 0.20:
                stage = "down"

            if diff < 0.18 and stage == "down":
                stage = "up"
                counter += 1

            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.putText(frame, f"Situps: {counter}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        cv2.imshow("Sit-up Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return counter

# -------------------------
# Streamlit UI
# -------------------------
st.title("🏃 AI Athlete Performance Evaluation System")

menu = st.sidebar.selectbox("Menu", ["Test", "Dashboard"])

# -------------------------
# TEST PAGE
# -------------------------
if menu == "Test":

    st.header("Sit-Up Performance Test")

    name = st.text_input("Name")
    age = st.number_input("Age", 10, 60)

    if st.button("Start Test"):

        if name == "":
            st.warning("Please enter your name.")
        else:
            reps = count_situps()

            if reps > 0:

                ai_score, grade = calculate_ai_score(age, reps)

                save_result(name, age, reps, grade)

                st.success(f"Total Reps: {reps}")
                st.info(f"AI Performance Score: {ai_score}/100")
                st.info(f"Fitness Grade: {grade}")

            else:
                st.error("No reps detected. Try again.")

# -------------------------
# DASHBOARD PAGE
# -------------------------
if menu == "Dashboard":

    st.header("Athlete Performance Dashboard")

    df = pd.read_sql_query(
        "SELECT * FROM results ORDER BY date DESC",
        conn
    )

    if len(df) > 0:

        st.dataframe(df)

        st.subheader("Performance Analytics")

        total_tests = len(df)
        avg_reps = df["reps"].mean()
        best_reps = df["reps"].max()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Tests", total_tests)
        col2.metric("Average Reps", round(avg_reps, 2))
        col3.metric("Best Performance", best_reps)

        st.divider()

        st.subheader("🏆 Top 5 Performers")
        top5 = df.sort_values(by="reps", ascending=False).head(5)
        st.dataframe(top5)

        st.divider()

        athlete = st.selectbox("Select Athlete", df["name"].unique())
        athlete_data = df[df["name"] == athlete]

        st.subheader(f"{athlete}'s Progress Over Time")
        st.line_chart(athlete_data["reps"])

        st.divider()

        st.subheader("Overall Repetition Distribution")
        st.bar_chart(df["reps"])

    else:
        st.write("No data yet.")
