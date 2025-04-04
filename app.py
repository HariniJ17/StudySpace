from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import os
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyspace.db'
db = SQLAlchemy(app)

# Database Path
DB_PATH = os.path.join(app.instance_path, "studyspace.db")
os.makedirs(app.instance_path, exist_ok=True)  # Ensure instance folder exists

# Uploads folder setup
UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Ensure the receipts directory exists
os.makedirs("receipts", exist_ok=True)

# Function to get DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Function to check file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_cost INTEGER NOT NULL,
            course_duration TEXT NOT NULL
        )
    """)
     # ✅ Insert courses only if they don’t exist
    courses = [
        ("Python Basics", 699, "4 Weeks"),
        ("Web Development", 299, "3 Weeks"),
        ("Data Manipulation", 599, "4 Weeks")
    ]

    for course in courses:
        cursor.execute("SELECT * FROM courses WHERE course_name = ?", (course[0],))
        if cursor.fetchone() is None:  # ✅ Check if course already exists
            cursor.execute("INSERT INTO courses (course_name, course_cost, course_duration) VALUES (?, ?, ?)", course)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            course_cost INTEGER NOT NULL,
            course_duration TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            module_name TEXT NOT NULL,
            module_description TEXT,
            video_url TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
    """)
    
    cursor.execute("SELECT id, username, course_name, course_cost FROM enrollments")
    enrollments = cursor.fetchall()

    # Calculate total revenue
    cursor.execute("SELECT SUM(course_cost) FROM enrollments")
    total_revenue = cursor.fetchone()[0] or 0  # Ensure it doesn't return None
    
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
#signup
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
            conn.close()  # ✅ Close before redirecting
            return redirect(url_for("login"))  # ✅ Redirect properly
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
            conn.close()  # ✅ Close before redirecting
            return redirect(url_for("signup"))  # ✅ Redirect back to signup if error

    return render_template("signup.html")


ADMIN_EMAIL = "studyspace796@gmail.com"
ADMIN_PASSWORD = "1234"  # Store securely in production

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True, default="default.jpg")  # Default profile pic
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)  # Relationship

# Course Model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    # description = db.Column(db.Text, nullable=False)
    # instructor = db.Column(db.String(100), nullable=False)
    modules = db.relationship('CourseModule', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)  # Relationship

# Course Module Model
class CourseModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    module_number = db.Column(db.Integer, nullable=False)
    module_title = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.String(300), nullable=False)

# Enrollment Model
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        if user_type == "admin":
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                session['admin'] = email
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid Admin Credentials!', 'danger')
                return redirect(url_for('login'))
        else:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session["username"] = user["username"]  # ✅ Store username in session
                session["user_id"] = user["id"]  # ✅ Store user ID for future reference
                return redirect(url_for('home'))  # ✅ Redirect to profile
            else:
                flash('Invalid Student Credentials!', 'danger')

    return render_template('login.html')


# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()

    # ✅ Fetch actual user data instead of just count
    users = conn.execute('SELECT * FROM users').fetchall()  
    courses = conn.execute('SELECT * FROM courses').fetchall()
    enrollments = conn.execute('SELECT * FROM enrollments').fetchall()
    
    # Calculate total revenue
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(course_cost) FROM enrollments")
    total_revenue = cursor.fetchone()[0] or 0  # Ensure it doesn't return None
    cursor.execute("""
    SELECT course_name, COUNT(*) as enrollments
    FROM enrollments
    GROUP BY course_name
    ORDER BY enrollments DESC
    LIMIT 5
""")
    top_courses = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users, courses=courses, enrollments=enrollments, total_revenue=total_revenue, top_courses=top_courses)

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
    course_id = 1  # Assuming Python course has ID 1 in your database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch course details
    cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
    course = cursor.fetchone()

    # Check if the user is enrolled
    enrolled = False
    if "username" in session:
        cursor.execute("SELECT * FROM enrollments WHERE username = ? AND course_id = ?", (session["username"], course_id))
        enrolled = bool(cursor.fetchone())

    conn.close()
    return render_template("python.html", course=course, enrolled=enrolled)

# Python courses
@app.route("/pycourse")
def pycourse():
    course_id = 1  # Python course ID
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch course modules or content
    cursor.execute("SELECT * FROM course_modules WHERE course_id = ?", (course_id,))
    modules = cursor.fetchall()

    conn.close()
    return render_template("pycourse.html", modules=modules)

# Web development course
@app.route("/webdev")
def webdev():
    course_id = 2  
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch course details
    cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
    course = cursor.fetchone()

    # Check if the user is enrolled
    enrolled = False
    if "username" in session:
        cursor.execute("SELECT * FROM enrollments WHERE username = ? AND course_id = ?", (session["username"], course_id))
        enrolled = bool(cursor.fetchone())

    conn.close()
    return render_template("web.html", course=course, enrolled=enrolled)

@app.route("/webdevcourse")
def webdevcourse():
    course_id = 2  # Python course ID
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch course modules or content
    cursor.execute("SELECT * FROM course_modules WHERE course_id = ?", (course_id,))
    modules = cursor.fetchall()

    conn.close()
    return render_template("webdevelop.html", modules=modules)

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')  # Create a quiz.html file in templates folder

@app.route('/data_manipulation')
def data_manipulation():
    id = session.get('id')  # Ensure user is logged in
    enrolled = False  # Default state
    if id:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if user is enrolled in course_id 10(Data Manipulation)
        cursor.execute("SELECT * FROM enrollments WHERE id = ? AND course_id = ?", (id, 10))
        enrollment = cursor.fetchone()
        if enrollment:
            enrolled = True  # User is enrolled
        conn.close()
    return render_template('datamanipulation.html', enrolled=enrolled)
@app.route('/Physics')
def Physics():
    id = session.get('id')  # Ensure user is logged in
    enrolled = False  # Default state
    if id:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if user is enrolled in course_id 11 (Data Manipulation)
        cursor.execute("SELECT * FROM enrollments WHERE id = ? AND course_id = ?", (id, 11))
        enrollment = cursor.fetchone()
        if enrollment:
            enrolled = True  # User is enrolled
        conn.close()
    return render_template('phy.html', enrolled=enrolled)

@app.route("/unit1")
def unit1():
    return render_template("unit1.html")
@app.route("/unit2")
def unit2():
    return render_template("unit2.html")
@app.route("/unit5")
def unit5():
    return render_template("unit5.html")
@app.route("/unit3")
def unit3():
    return render_template("unit3.html")
@app.route("/unit4")
def unit4():
    return render_template("unit4.html")
@app.route("/theoryquiz")
def theoryquiz():
    return render_template("theoryquiz.html")

@app.route('/enroll', methods=['POST', 'GET'])
def enroll():
    if "username" not in session:
        flash("You must be logged in to enroll!", "warning")
        return redirect(url_for("login"))

    username = session["username"]

    # 🔹 Fetch course details from POST form or GET URL parameters
    if request.method == 'POST':
        course_id = request.form.get('course_id', "").strip()
        course_name = request.form.get('course_name', "Unknown Course").strip()
        course_cost = request.form.get('course_cost', "0").strip()
        course_duration = request.form.get('course_duration', "Unknown Duration").strip()
    else:
        course_id = request.args.get('course_id', "").strip()
        course_name = request.args.get('course_name', "Unknown Course").strip()
        course_cost = request.args.get('course_cost', "0").strip()
        course_duration = request.args.get('course_duration', "Unknown Duration").strip()

    # 🔹 Validate `course_id`
    if not course_id.isdigit():
        flash("Invalid course ID!", "danger")
        return redirect(url_for("courses"))

    course_id = int(course_id)  # Convert to integer

    # 🔹 Validate `course_cost`
    try:
        course_cost = int(course_cost)
    except ValueError:
        flash("Invalid course cost!", "danger")
        return redirect(url_for("courses"))

    # 🔹 Database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user is already enrolled
    cursor.execute("SELECT 1 FROM enrollments WHERE username = ? AND course_id = ?", (username, course_id))
    already_enrolled = cursor.fetchone()

    if already_enrolled:
        flash(f"You are already enrolled in {course_name}!", "info")
    else:
        cursor.execute("""
            INSERT INTO enrollments (username, course_id, course_name, course_cost, course_duration) 
            VALUES (?, ?, ?, ?, ?)
        """, (username, course_id, course_name, course_cost, course_duration))
        conn.commit()
        flash(f"Successfully enrolled in {course_name}!", "success")

    conn.close()

    # 🔹 Redirect Logic
    if course_cost > 0:
        return redirect(url_for('payment', 
                                course_id=course_id, 
                                course_name=course_name, 
                                course_cost=course_cost, 
                                course_duration=course_duration))
    else:
        return redirect(url_for('data_manipulation' if course_id == 10 else 'courses'))  # Adjust based on your logic
    
@app.route('/certificate', methods=["GET"])
def certificate():
    username = session.get("username")

    if not username:
        return "User not logged in.", 400

    # Connect to the database
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # Ensure dictionary-style row access
    cursor = conn.cursor()

    # Fetch the latest purchased course for the user
    cursor.execute("""
        SELECT course_name 
        FROM enrollments 
        WHERE username = ? 
        LIMIT 1
    """, (username,))
    
    course_data = cursor.fetchone()
    conn.close()

    if not course_data:
        return "No course found for this user.", 400

    # Extract course name correctly
    course_name = course_data["course_name"]  # Access by column name
    completion_date = datetime.now().strftime("%Y-%m-%d")  # Use today's date

    return render_template('certificate.html', 
                           username=username, 
                           course_name=course_name, 
                           completion_date=completion_date)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if "username" not in session:
        flash("You must be logged in to continue!", "warning")
        return redirect(url_for("login"))

    course_id = request.args.get('course_id')
    course_name = request.args.get('course_name', "Unknown Course")
    course_cost = request.args.get('course_cost', "0")
    course_duration = request.args.get('course_duration', "Unknown Duration")

    if request.method == 'POST':
        # Assuming payment is successful, redirect to invoice
        return redirect(url_for('invoice',
                                course_id=course_id,
                                course_name=course_name,
                                course_cost=course_cost,
                                course_duration=course_duration))

    return render_template('payment.html', 
                           course_id=course_id, 
                           course_name=course_name, 
                           course_cost=course_cost, 
                           course_duration=course_duration)

@app.route('/confirm_payment', methods=["GET"])
def confirm_payment():
    # Get data from query parameters
    course_name = request.args.get('course_name')  
    course_cost = request.args.get('course_cost')
    course_duration = request.args.get('course_duration')
    course_id = request.args.get('course_id')

    # Ensure user is logged in
    username = session.get("username")
    if not username:
        flash("Please log in to view your payment confirmation.", "warning")
        return redirect(url_for("login"))

    # Fetch the enrolled course details securely
    conn = None
    enrolled_course = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM enrollments 
            WHERE username = ? AND course_id = ?
        """, (username, course_id))
        enrolled_course = cursor.fetchone()
    except Exception as e:
        flash("An error occurred while retrieving your enrollment details.", "danger")
        print("Database Error:", str(e))
    finally:
        if conn:
            conn.close()

    if not enrolled_course:
        flash("Enrollment not found! Please check your courses.", "danger")
        return redirect(url_for("courses"))

    return render_template('payment_confirmation.html', 
                           course_name=course_name, 
                           course_cost=course_cost, 
                           course_duration=course_duration,
                           course_id=course_id,
                           enrolled_course=enrolled_course)

# Payment Process
@app.route('/process_payment', methods=['POST'])
def process_payment():
    course_name = request.form.get('course_name')
    course_cost = request.form.get('course_cost')
    course_duration = request.form.get('course_duration')
    course_id = request.form.get('course_id')
    card_number = request.form.get('card_number')
    expiry_date = request.form.get('expiry_date')
    cvv = request.form.get('cvv')

    # Validate Card Number (Should be 12-16 digits)
    if not card_number.isdigit() or len(card_number) < 12 or len(card_number) > 16:
        return "Invalid Card Number! Please enter a valid 12-16 digit card number."

    # Validate CVV (Should be 3 digits)
    if not cvv.isdigit() or len(cvv) != 3:
        return "Invalid CVV! Please enter a valid 3-digit CVV."

    # Validate Expiry Date (Should be MM/YY and between 2025-2045)
    try:
        exp_month, exp_year = expiry_date.split('/')
        exp_month = int(exp_month)
        exp_year = int("20" + exp_year)  # Convert YY to YYYY

        if exp_month < 1 or exp_month > 12:
            return "Invalid Expiry Date! Month must be between 01 and 12."

        if exp_year < 2025 or exp_year > 2045:
            return "Invalid Expiry Year! Must be between 2025 and 2045."

    except:
        return "Invalid Expiry Date format! Use MM/YY format."

    # ✅ Pass data using query parameters
    return redirect(url_for('confirm_payment', 
                            course_name=course_name, 
                            course_cost=course_cost, 
                            course_duration=course_duration,
                            course_id=course_id))

@app.route('/invoice', methods=["GET"])
def invoice():
    course_id = request.args.get('course_id')
    course_name = request.args.get('course_name', "Unknown Course")
    course_cost = request.args.get('course_cost', "0")
    course_duration = request.args.get('course_duration', "Unknown Duration")
    username = session.get("username")
    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # If course_name or cost is missing, fetch from DB
    if course_name == "Unknown Course" or course_cost == "0":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_name, course_cost, course_duration FROM enrollments WHERE username = ? AND course_id = ?", 
                       (username, course_id))
        course_data = cursor.fetchone()
        conn.close()

        if course_data:
            course_name, course_cost, course_duration = course_data
            
        # Save invoice details in session for later use in certificate
        session['certificate_data'] = {
            'username': username,
            'course_name': course_name,
            'purchase_date': purchase_date
        }

    return render_template('invoice.html', 
                           course_name=course_name, 
                           course_cost=course_cost, 
                           course_duration=course_duration, 
                           course_id=course_id,
                           username=username,
                           purchase_date=purchase_date)

@app.route('/download_invoice')
def download_invoice():
    course_id = request.args.get('course_id', 'Unknown ID')
    course_name = request.args.get('course_name', 'Unknown Course')
    course_cost = request.args.get('course_cost', '0')
    course_duration = request.args.get('course_duration', 'Unknown Duration')
    purchase_date = request.args.get('purchase_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    username = session.get("username")

    if course_name == "Unknown Course" or course_cost == "0":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_name, course_cost, course_duration FROM enrollments WHERE username = ? AND course_id = ?", 
                       (username, course_id))
        course_data = cursor.fetchone()
        conn.close()

        if course_data:
            course_name, course_cost, course_duration = course_data

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Invoice")

    pdf.drawString(100, 750, "Invoice")
    pdf.drawString(100, 730, f"User: {username}")
    pdf.drawString(100, 710, f"Course Name: {course_name}")
    pdf.drawString(100, 690, f"Course Cost: ₹{course_cost}")
    pdf.drawString(100, 670, f"Course Duration: {course_duration}")
    pdf.drawString(100, 650, f"Purchase Date: {purchase_date}")

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=invoice.pdf'
    return response


@app.route('/profile')
def profile():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
    
    username = session["username"]
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    enrollments = conn.execute('SELECT * FROM enrollments WHERE username = ?', (username,)).fetchall()
    conn.close()
    
    if not user_data:
        flash("User not found!", "danger")
        return redirect(url_for("login"))
    return render_template('profile.html', user=user_data, enrollments=enrollments)

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

@app.route("/htmldebugging")
def htmldebugging():
    return render_template("htmldebugging.html")
@app.route("/jsdebugging")
def jsdebugging():
    return render_template("jsdebugging.html")
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
