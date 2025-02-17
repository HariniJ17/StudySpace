import sqlite3

# Database file path
DB_FILE = 'users.db'

def update_database():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check and add missing columns to the 'users' table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_photo TEXT DEFAULT 'static/uploads/default_profile.png'")
    except sqlite3.OperationalError:
        print("Column 'profile_photo' already exists.")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        print("Column 'bio' already exists.")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN skills TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        print("Column 'skills' already exists.")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN courses TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        print("Column 'courses' already exists.")

    # Update existing rows with default values for new columns
    cursor.execute("UPDATE users SET profile_photo = 'static/uploads/default_profile.png' WHERE profile_photo IS NULL")
    cursor.execute("UPDATE users SET bio = '' WHERE bio IS NULL")
    cursor.execute("UPDATE users SET skills = '' WHERE skills IS NULL")
    cursor.execute("UPDATE users SET courses = '' WHERE courses IS NULL")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database update complete!")

if __name__ == "__main__":
    update_database()
