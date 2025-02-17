import sqlite3
conn = sqlite3.connect("studyspace.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Create courses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)
""")

# Create enrollments table (for passbook)
cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    course_name TEXT NOT NULL,
    amount INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("INSERT INTO courses (name, price) VALUES ('Python Basics', 499)")
cursor.execute("INSERT INTO courses (name, price) VALUES ('Cloud Computing', 999)")
conn.commit()
conn.close()

print("Database initialized successfully!")
