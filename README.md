🏃 AI Athlete Performance Evaluation System

📌 Project Overview

This project is an AI-based system that evaluates athlete performance using real-time pose estimation. It detects exercises like sit-ups and push-ups using computer vision and provides performance analytics.

🚀 Features

 ✅ Real-time exercise detection (Sit-ups & Push-ups)
 ✅ Angle-based motion analysis using MediaPipe
 ✅ Posture correctness scoring
 ✅ Automated repetition counting
 ✅ Fraud detection system (anti-cheating)
 ✅ Performance grading system
 ✅ Dashboard with analytics & leaderboard
 ✅ SQLite database integration


 🧠 Technologies Used

 Python
 OpenCV
 MediaPipe
 Streamlit
 SQLite
 NumPy
 Pandas


 ⚙️ How It Works

1. Webcam captures live video
2. MediaPipe detects body landmarks
3. Joint angles are calculated
4. Repetitions are counted based on motion
5. Posture accuracy is evaluated
6. Fraud detection checks abnormal patterns
7. Results are stored and displayed in dashboard



🛡️ Fraud Detection

The system detects cheating using:

 Frame freeze detection (no movement)
 Motion analysis (frame difference)
 Angle consistency check (detects fake repetitive motion)



📊 Output

 Repetition count
 Posture score (%)
 Performance grade
 Dashboard analytics



▶️ Run the Project

streamlit run app.py

👨‍💻 Author

Devang Sharma
Registration No: 2427030731


🎓 Mentor

Dr. Mayank Namdev

🏫 Institution

Manipal University Jaipur
Department of Computer Science & Engineering

---
