import sqlite3
import os

# Database Path
DB_PATH = os.path.join("instance", "studyspace.db")
os.makedirs("instance", exist_ok=True)  # Ensure instance folder exists

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_pic TEXT DEFAULT 'default.png'
    )
""")


# Create Courses Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        instructor TEXT
    )
""")

# Create Enrollments Table (With course_name column)
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
# Commit and close the connection
conn.commit()
conn.close()

print("Database initialized successfully!")
