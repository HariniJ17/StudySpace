from flask import Flask, request, render_template, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

# Initialize Database
def init_db():
    with sqlite3.connect('progress.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY,
                completed_videos INTEGER,
                progress INTEGER
            )
        ''')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/notes')
def notes():
    return "<h2>📝 This is the Notes Page</h2>"

@app.route('/comments')
def comments():
    return "<h2>💬 This is the Comments Page</h2>"

@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    progress = data['progress']
    completed_videos = int(progress / 20)

    with sqlite3.connect('progress.db') as conn:
        conn.execute('''
            INSERT OR REPLACE INTO progress (id, completed_videos, progress)
            VALUES (1, ?, ?)
        ''', (completed_videos, progress))
        conn.commit()

    return jsonify({"status": "success"})

@app.route('/get_progress', methods=['GET'])
def get_progress():
    with sqlite3.connect('progress.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT completed_videos, progress FROM progress WHERE id = 1')
        data = cursor.fetchone()
        return jsonify({"completed_videos": data[0], "progress": data[1]})

# New Route to Serve the Certificate

from flask import Flask, request, render_template, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

# Initialize Database
def init_db():
    with sqlite3.connect('progress.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY,
                completed_videos INTEGER,
                progress INTEGER
            )
        ''')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/notes')
def notes():
    return "<h2>📝 This is the Notes Page</h2>"

@app.route('/comments')
def comments():
    return "<h2>💬 This is the Comments Page</h2>"

@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    progress = data['progress']
    completed_videos = int(progress / 20)

    with sqlite3.connect('progress.db') as conn:
        conn.execute('''
            INSERT OR REPLACE INTO progress (id, completed_videos, progress)
            VALUES (1, ?, ?)
        ''', (completed_videos, progress))
        conn.commit()

    return jsonify({"status": "success"})

@app.route('/get_progress', methods=['GET'])
def get_progress():
    with sqlite3.connect('progress.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT completed_videos, progress FROM progress WHERE id = 1')
        data = cursor.fetchone()
        return jsonify({"completed_videos": data[0], "progress": data[1]})

# New Route to Serve the Certificate
@app.route('/certificate')
def certificate():
    return render_template('certificate.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
