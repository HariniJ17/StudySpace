from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Path
DB_PATH = os.path.join(app.instance_path, "studyspace.db")
os.makedirs(app.instance_path, exist_ok=True)  # Ensure instance folder exists

# Uploads folder setup
UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to get DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Function to check file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Create tables (Run once at startup)
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_pic TEXT DEFAULT 'default.png'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            instructor TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    conn.commit()
    conn.close()

# First Page
@app.route("/")
def logo():
    return render_template("logo.html")
#Home page
@app.route("/home")
def home():
    return render_template("home/index.html")  # Explicitly mention the subfolder


# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, password))
            conn.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
        finally:
            conn.close()

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user:
            flash("No account found with this email!", "danger")
        elif not check_password_hash(user["password"], password):
            flash("Incorrect password. Please try again!", "danger")
        else:
            session["username"] = user["username"]
            session["email"] = user["email"]
            return redirect(url_for("profile"))

    return render_template("login.html")

# Courses Page
@app.route("/courses")
def courses():
    conn = get_db_connection()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()
    return render_template("course.html", courses=courses)

# Python course
@app.route("/python")
def python():
    return render_template("python.html")

# Enroll Route
@app.route("/enroll/<int:course_id>/<course_name>")
def enroll(course_id, course_name):
    if "username" not in session:
        flash("You must be logged in to enroll!", "warning")
        return redirect(url_for("login"))

    username = session["username"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already enrolled
    cursor.execute("SELECT * FROM enrollments WHERE username = ? AND course_id = ?", (username, course_id))
    if cursor.fetchone():
        flash(f"You are already enrolled in {course_name}!", "info")
    else:
        cursor.execute("INSERT INTO enrollments (username, course_id, course_name) VALUES (?, ?, ?)", 
                       (username, course_id, course_name))
        conn.commit()
        flash(f"Successfully enrolled in {course_name}!", "success")

    conn.close()
    return redirect(url_for("profile"))

# Profile Page
@app.route("/profile" , methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    user_data = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    enrollments = conn.execute("SELECT * FROM enrollments WHERE username = ?", (username,)).fetchall()
    conn.close()

    if not user_data:
        flash("User not found!", "danger")
        return redirect(url_for("login"))

    return render_template("profile.html", user=user_data, enrollments=enrollments)

# Upload Profile Picture Route
@app.route("/upload_profile_pic", methods=["POST"])
def upload_profile_pic():
    if "username" not in session:
        flash("You must be logged in!", "danger")
        return redirect(url_for("login"))

    if "profile_pic" not in request.files:
        flash("No file uploaded!", "warning")
        return redirect(url_for("profile"))

    file = request.files["profile_pic"]
    if file.filename == "":
        flash("No selected file!", "warning")
        return redirect(url_for("profile"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Update database with new profile picture
        username = session["username"]
        conn = get_db_connection()
        conn.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (filename, username))
        conn.commit()
        conn.close()

        flash("Profile picture updated!", "success")
    else:
        flash("Invalid file type!", "danger")

    return redirect(url_for("profile"))
# Edit Profile Route
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        flash("You must be logged in!", "danger")
        return redirect(url_for("login"))

    username = session["username"]
    conn = get_db_connection()
    user_data = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]

        conn.execute("UPDATE users SET username = ?, email = ? WHERE username = ?", 
                     (new_username, new_email, username))
        conn.commit()
        conn.close()

        # Update session with new username
        session["username"] = new_username
        session["email"] = new_email

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    conn.close()
    return render_template("edit_profile.html", user=user_data)

#Game
@app.route("/game")
def game():
    return render_template("game.html")
                                               #GAMES
#cyber
@app.route('/cyber')
def cyber():
    return render_template('cyber.html')

#memory
@app.route('/memory')
def memory():
    return render_template('memorycard.html')

#word
@app.route('/word')
def word():
    return render_template('word.html')
#tech
@app.route('/tech')
def tech():
    return render_template('tech.html')
#maths
@app.route('/maths')
def maths():
    return render_template('maths.html')
#fraction
@app.route('/fraction')
def fraction():
    return render_template('frac.html')
#chemistry
@app.route('/chemistry')
def chemistry():
    return render_template('che.html')
#grammar
@app.route('/grammar')
def grammar():
    return render_template('grammar.html')
#vocubalary
@app.route('/vocubalary')
def vocubalary():
    return render_template('vol.html')

# Contact Page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Run the App
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
