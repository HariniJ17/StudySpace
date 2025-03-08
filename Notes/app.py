from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

# Create database & notes table if not exists
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            note TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route("/course/<int:course_id>")
def course_page(course_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT note, timestamp FROM notes WHERE course_id=?", (course_id,))
    notes = cursor.fetchall()
    conn.close()

    return render_template("course.html", notes=notes)

@app.route("/save_note", methods=["POST"])
def save_note():
    note = request.form["note"]
    course_id = request.form["course_id"]
    user_id = 1  # Change this to the logged-in user's ID

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, course_id, note) VALUES (?, ?, ?)", (user_id, course_id, note))
    conn.commit()
    conn.close()

    return redirect(f"/course/{course_id}")

if __name__ == "__main__":
    init_db()
    
    app.run(debug=True, port=5000)

