from flask import Flask, request, render_template, redirect,session, url_for, flash
import sqlite3

app = Flask(__name__)

# Ensure database exists
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            username TEXT,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route("/course/<int:course_id>", methods=["GET", "POST"])
def course_page(course_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Save new comment
    if request.method == "POST":
        username = request.form.get("username")
        comment = request.form.get("comment")
        cursor.execute("INSERT INTO comments (course_id, username, comment) VALUES (?, ?, ?)",
                       (course_id, username, comment))
        conn.commit()

    # Fetch comments for the course
    cursor.execute("SELECT username, comment, timestamp FROM comments WHERE course_id=?", (course_id,))
    comments = cursor.fetchall()
    conn.close()

    return render_template("course.html", course_id=course_id, comments=comments)

@app.route("/add_comment/<int:course_id>", methods=["GET", "POST"])
def add_comment(course_id):
    if "email" not in session:
        flash("You must be logged in to comment!", "warning")
        return redirect(url_for("login"))

    email = session["email"]
    comment = request.form["comment"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (course_id, email, comment) VALUES (?, ?, ?)", 
                   (course_id, email, comment))
    conn.commit()
    conn.close()

    flash("Comment added successfully!", "success")
    return redirect(url_for("course_page", course_id=course_id))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
