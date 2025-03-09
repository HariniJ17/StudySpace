from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    timestamp TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('quiz.html')

@app.route('/submit', methods=['POST'])
def submit_quiz():
    user_name = request.form.get('user_name')
    score = 0
    total_questions = 3

    answers = {
        'q1': 'a',
        'q2': 'c',
        'q3': 'a'
    }

    for i in range(1, total_questions + 1):
        selected_answer = request.form.get(f'q{i}')
        if selected_answer == answers[f'q{i}']:
            score += 1

    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute("INSERT INTO results (user_name, score, total_questions, timestamp) VALUES (?, ?, ?, ?)",
              (user_name, score, total_questions, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return redirect(url_for('quiz_result', score=score, total_questions=total_questions))

@app.route('/result')
def quiz_result():
    score = int(request.args.get('score'))
    total_questions = int(request.args.get('total_questions'))
    return render_template('result.html', score=score, total_questions=total_questions)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)