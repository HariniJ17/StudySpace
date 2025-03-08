from flask import Flask, request, render_template, jsonify, send_file
import sqlite3
from fpdf import FPDF
import os

app = Flask(__name__)

# Database Setup
def init_db():
    with sqlite3.connect('progress.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS progress (
                            id INTEGER PRIMARY KEY,
                            video_id INTEGER,
                            progress INTEGER,
                            quiz_score INTEGER
                        )''')

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Update progress and quiz score
@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    video_id = data['video_id']
    progress = data['progress']
    quiz_score = data['quiz_score']

    with sqlite3.connect('progress.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO progress (id, video_id, progress, quiz_score)
                          VALUES (1, ?, ?, ?)''', (video_id, progress, quiz_score))
        conn.commit()

    return jsonify({"status": "success", "progress": progress, "quiz_score": quiz_score})

# Get progress data
@app.route('/get_progress', methods=['GET'])
def get_progress():
    with sqlite3.connect('progress.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT video_id, progress, quiz_score FROM progress')
        progress_data = cursor.fetchall()
        return jsonify(progress_data)

# Generate certificate when course is completed
@app.route('/generate_certificate', methods=['GET'])
def generate_certificate():
    with sqlite3.connect('progress.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT progress, quiz_score FROM progress')
        progress_data = cursor.fetchall()

        # Check if all progress is 100% and quiz score is 100%
        if all(progress == 100 and quiz_score == 100 for _, progress, quiz_score in progress_data):
            # Generate Certificate
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="E-learning Platform Certificate", ln=True, align="C")
            pdf.cell(200, 10, txt="Congratulations! You've completed the course.", ln=True, align="C")
            pdf.output("static/certificate.pdf")
            return send_file("static/certificate.pdf", as_attachment=True)

        return jsonify({"status": "incomplete", "message": "Complete all videos and quizzes to receive the certificate."})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
