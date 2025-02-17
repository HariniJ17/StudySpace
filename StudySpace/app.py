from flask import Flask, render_template, request, redirect, jsonify ,flash ,session ,url_for
import sqlite3

app = Flask(__name__)

# Homepage (Course List)
@app.route('/')
def home():
    conn = sqlite3.connect("studyspace.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return render_template('index.html', courses=courses)

# Enrollment route
@app.route('/enroll', methods=['POST'])
def enroll():
    if 'user_id' not in session:
        return jsonify({"message": "You must be logged in to enroll"}), 401

    data = request.get_json()
    course_name = data.get('course')

    if not course_name:
        return jsonify({"message": "Course name is required"}), 400

    user_id = session['user_id']
    username = session['username']
    email = session['email']  # Fetch email from session

    # Connect to SQLite database and store enrollment
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create enrollment table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS enrollment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username TEXT,
                        email TEXT,
                        course_name TEXT,
                        UNIQUE(user_id, course_name)
                    )''')

    try:
        cursor.execute("INSERT INTO enrollment (user_id, username, email, course_name) VALUES (?, ?, ?, ?)",
                       (user_id, username, email, course_name))
        conn.commit()
        flash(f"Enrolled in {course_name} successfully!", "success")
    except sqlite3.IntegrityError:
        flash("You are already enrolled in this course!", "error")
    finally:
        conn.close()

    return jsonify({"redirect_url": url_for('profile')})


@app.route('/admin')
def admin_panel():
    conn = sqlite3.connect("studyspace.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM enrollments")  # Fetch all enrolled users
    enrollments = cursor.fetchall()
    conn.close()
    return render_template('admin.html', enrollments=enrollments)


if __name__ == '__main__':
    app.run(debug=True)
