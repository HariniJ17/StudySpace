from flask import Flask, render_template, request, redirect, url_for, session, flash 
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure random string

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        profile_photo TEXT DEFAULT 'static/uploads/default_profile.png',
                        bio TEXT DEFAULT '',
                        skills TEXT DEFAULT '',
                        courses TEXT DEFAULT ''
                    )''')
    conn.commit()
    conn.close()

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate password
        if len(password) < 6 or not any(char.isalpha() for char in password) or not any(char in '!@#$%^&*()_+' for char in password):
            flash("Password must be at least 6 characters long, contain letters, and include at least one special character.", "error")
            return redirect(url_for('signup'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Connect to SQLite database and insert the user data
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            conn.commit()

            # Automatically log in the user after signup
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username
            session['email'] = email
            session['profile_photo'] = 'static/uploads/default_profile.png'
            session['bio'] = ''
            session['skills'] = []

            flash("Signup successful! Welcome to your profile.", "success")
            return redirect(url_for('profile'))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "error")
        finally:
            conn.close()

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to SQLite database and fetch the user data by username
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):  # user[3] is the hashed password column
            # Store user details in the session
            session['user_id'] = user[0]  # user[0] is the user ID column
            session['username'] = user[1]
            session['email'] = user[2]
            session['profile_photo'] = 'static/uploads/default_profile.png' # Default photo
            session['bio'] = user[5]
            session['skills'] = user[6]
            flash("Login successful!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Invalid credentials, please try again.", "error")
            return "<script>alert('Invalid username or password!'); window.location.href='/login';</script>"

    return render_template('login.html')

# Profile route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("You must log in to view this page.", "error")
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, profile_photo, bio, skills, courses FROM users WHERE id=?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    user_data = {
        'username': user[0],
        'email': user[1],
        'profile_photo_url': user[2],
        'bio': user[3],
        'skills': user[4].split(',') if user[4] else [],
        'courses': eval(user[5]) if user[5] else []  # Assuming courses are stored as JSON strings
    }

    return render_template('profile.html', user=user_data)

# Edit Profile Photo route
@app.route('/edit-photo', methods=['POST'])
def edit_photo():
    if 'user_id' not in session:
        flash("You must log in to update your profile photo.", "error")
        return redirect(url_for('login'))

    profile_photo = request.files.get('profile_photo')

    if profile_photo and allowed_file(profile_photo.filename):
        filename = secure_filename(profile_photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_photo.save(filepath)

        # Update profile photo in the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_photo=? WHERE id=?", (filepath, session['user_id']))
        conn.commit()
        conn.close()

        # Update session variable
        session['profile_photo'] = filepath

        flash("Profile photo updated successfully!", "success")
    else:
        flash("Invalid file type. Please upload an image file.", "error")

    return redirect(url_for('profile'))

# Edit Profile route
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("You must log in to update your profile.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username', session['username'])
        bio = request.form.get('bio', '')
        skills = request.form.get('skills', '')

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the username is already taken by another user
        cursor.execute("SELECT id FROM users WHERE username=? AND id!=?", (username, session['user_id']))
        if cursor.fetchone():
            flash("Username already exists. Please choose another one.", "error")
            return redirect(url_for('profile'))

        # Update other profile details
        cursor.execute("UPDATE users SET username=?, bio=?, skills=? WHERE id=?", 
                       (username, bio, skills, session['user_id']))
        conn.commit()
        conn.close()

        # Update session variables
        session['username'] = username
        session['bio'] = bio
        session['skills'] = skills.split(',') if skills else []

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user={
        'username': session['username'],
        'bio': session.get('bio', ''),
        'skills': ','.join(session.get('skills', []))
    })

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()  # Initialize the database
    app.run(debug=True)
