import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import sqlite3
import pandas as pd
from datetime import datetime

# CONFIG
st.set_page_config(layout="wide")

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# DATABASE
conn = sqlite3.connect("fitness.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS results (
    name TEXT,
    age INTEGER,
    reps INTEGER,
    grade TEXT,
    date TEXT
)
""")

# Safe column add
try:
    c.execute("ALTER TABLE results ADD COLUMN posture REAL")
except:
    pass

conn.commit()

# UTIL
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

def get_grade(reps):
    if reps >= 20:
        return "Excellent"
    elif reps >= 15:
        return "Good"
    elif reps >= 10:
        return "Average"
    else:
        return "Needs Improvement"

# FIXED FRAUD DETECTION
def detect_fraud(angle_history, frame, prev_frame, freeze_counter):

    fraud = False

    if prev_frame is not None:
        diff = cv2.absdiff(prev_frame, frame)
        motion_score = np.sum(diff)

        if motion_score < 50000:
            freeze_counter += 1
        else:
            freeze_counter = 0

        if freeze_counter > 80:
            fraud = True

    if len(angle_history) > 30:
        if np.std(angle_history[-30:]) < 1.0:
            fraud = True

    return fraud, freeze_counter

# SITUPS
def count_situps():
    cap = cv2.VideoCapture(0)

    counter = 0
    stage = None
    correct = 0
    frames = 0

    angle_history = []
    prev_frame = None
    freeze_counter = 0
    fraud_flag = False

    with mp_pose.Pose() as pose:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frames += 1

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark

                shoulder = [lm[11].x, lm[11].y]
                hip = [lm[23].x, lm[23].y]
                knee = [lm[25].x, lm[25].y]

                angle = calculate_angle(shoulder, hip, knee)
                angle_history.append(angle)

                fraud, freeze_counter = detect_fraud(angle_history, frame, prev_frame, freeze_counter)
                if fraud:
                    fraud_flag = True

                if angle > 150:
                    stage = "down"

                if angle < 100 and stage == "down":
                    stage = "up"
                    counter += 1

                if 70 < angle < 120:
                    correct += 1

                mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            prev_frame = frame.copy()

            cv2.putText(frame, f"Sit-ups: {counter}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2)

            if fraud_flag:
                cv2.putText(frame, "FRAUD DETECTED", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            cv2.imshow("Sit-ups", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    posture = (correct / frames) * 100 if frames else 0
    return counter, posture, fraud_flag

# PUSHUPS
def count_pushups():
    cap = cv2.VideoCapture(0)

    counter = 0
    stage = None
    correct = 0
    frames = 0

    angle_history = []
    prev_frame = None
    freeze_counter = 0
    fraud_flag = False

    with mp_pose.Pose() as pose:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frames += 1

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark

                shoulder = [lm[11].x, lm[11].y]
                elbow = [lm[13].x, lm[13].y]
                wrist = [lm[15].x, lm[15].y]

                angle = calculate_angle(shoulder, elbow, wrist)
                angle_history.append(angle)

                fraud, freeze_counter = detect_fraud(angle_history, frame, prev_frame, freeze_counter)
                if fraud:
                    fraud_flag = True

                if angle > 160:
                    stage = "up"

                if angle < 90 and stage == "up":
                    stage = "down"
                    counter += 1

                if 80 < angle < 120:
                    correct += 1

                mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            prev_frame = frame.copy()

            cv2.putText(frame, f"Push-ups: {counter}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

            if fraud_flag:
                cv2.putText(frame, "FRAUD DETECTED", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            cv2.imshow("Push-ups", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    posture = (correct / frames) * 100 if frames else 0
    return counter, posture, fraud_flag

# UI
menu = st.sidebar.selectbox("Menu", ["Test", "Dashboard"])

st.title("🏃 AI Athlete Performance Evaluation System")

# TEST
if menu == "Test":

    st.header("Performance Test")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name")
        age = st.number_input("Age", 10, 60)

    with col2:
        exercise = st.selectbox("Exercise", ["Sit-ups", "Push-ups"])

    if st.button("Start Test"):

        if not name:
            st.warning("Enter name first")

        else:
            if exercise == "Sit-ups":
                reps, posture, fraud = count_situps()
            else:
                reps, posture, fraud = count_pushups()

            grade = get_grade(reps)

            if fraud:
                grade = "Fraud Detected"

            c.execute("""
            INSERT INTO results (name, age, reps, grade, posture, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (name, age, reps, grade, posture, str(datetime.now())))

            conn.commit()

            st.success(f"{exercise} Completed: {reps} reps")
            st.info(f"Posture Score: {round(posture,2)}%")
            st.warning(f"Status: {grade}")

# DASHBOARD
elif menu == "Dashboard":

    st.header("Athlete Performance Dashboard")

    df = pd.read_sql_query("SELECT * FROM results", conn)

    st.dataframe(df)

    if not df.empty:

        st.subheader("Performance Analytics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tests", len(df))
        col2.metric("Average Reps", round(df["reps"].mean(), 2))
        col3.metric("Best Performance", df["reps"].max())

        st.subheader("Grade Distribution")
        st.bar_chart(df["grade"].value_counts())

        st.subheader("Leaderboard")
        st.dataframe(df.sort_values(by="reps", ascending=False).head(5))
