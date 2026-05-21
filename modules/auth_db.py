# File: authentilearn/modules/auth_db.py
import sqlite3
import hashlib
import os
import json
import time
import secrets

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database.db"))

def init_db(db_path=DB_FILE):
    """
    Initializes the SQLite database and creates the students table if it doesn't exist.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            username TEXT PRIMARY KEY,
            student_id TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            biometrics_json TEXT,
            created_at REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            enrollment_key TEXT NOT NULL,
            description TEXT,
            topics TEXT,
            created_by TEXT,
            created_at REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            username TEXT NOT NULL,
            course_id TEXT NOT NULL,
            enrolled_at REAL NOT NULL,
            PRIMARY KEY (username, course_id),
            FOREIGN KEY (username) REFERENCES students(username),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)
    conn.commit()
    conn.close()

def generate_salt():
    """Generates a secure cryptographically random hex salt."""
    return secrets.token_hex(16)

def hash_password(password, salt):
    """Generates a secure SHA-256 hash from password and salt combination."""
    salted = password + salt
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def register_student(username, student_id, password, db_path=DB_FILE):
    """
    Registers a new student account in the database.
    Returns: (success_bool, message_str)
    """
    username = username.strip().lower()
    student_id = student_id.strip()
    
    if not username or not student_id or not password:
        return False, "All fields are required."
        
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if username exists
        cursor.execute("SELECT username FROM students WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already taken."
            
        # Check if student ID exists
        cursor.execute("SELECT username FROM students WHERE student_id = ?", (student_id,))
        if cursor.fetchone():
            conn.close()
            return False, "Student Registration ID already registered."
            
        # Save credentials
        salt = generate_salt()
        pwd_hash = hash_password(password, salt)
        created_at = time.time()
        
        cursor.execute("""
            INSERT INTO students (username, student_id, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, student_id, pwd_hash, salt, created_at))
        
        conn.commit()
        conn.close()
        return True, "Account registered successfully! You can now log in."
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}"

def authenticate_student(username, password, db_path=DB_FILE):
    """
    Authenticates a student by matching credentials.
    Returns: (success_bool, result_dict_or_error_msg)
    """
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
        
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT student_id, password_hash, salt, biometrics_json 
            FROM students WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False, "Invalid username or password."
            
        student_id, saved_hash, salt, biometrics_json = row
        input_hash = hash_password(password, salt)
        
        if input_hash == saved_hash:
            user_data = {
                "username": username,
                "student_id": student_id,
                "biometrics": json.loads(biometrics_json) if biometrics_json else None
            }
            return True, user_data
        else:
            return False, "Invalid username or password."
    except Exception as e:
        conn.close()
        return False, f"Authentication error: {str(e)}"

def save_student_biometrics(username, biometrics_dict, db_path=DB_FILE):
    """
    Saves or updates biometric signatures for a student account.
    Returns: success_bool
    """
    username = username.strip().lower()
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        biometrics_json = json.dumps(biometrics_dict)
        cursor.execute("""
            UPDATE students 
            SET biometrics_json = ? 
            WHERE username = ?
        """, (biometrics_json, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to save biometrics: {str(e)}")
        conn.close()
        return False

def load_student_biometrics(username, db_path=DB_FILE):
    """
    Loads biometric profiles for a student account.
    Returns: biometrics_dict or None
    """
    username = username.strip().lower()
    init_db(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT biometrics_json FROM students WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return json.loads(row[0])
        return None
    except Exception as e:
        print(f"Failed to load biometrics: {str(e)}")
        conn.close()
        return None

# ===================== Course Management Functions =====================

def create_course(course_id, course_name, enrollment_key, description="", topics="", created_by="educator", db_path=DB_FILE):
    """
    Creates a new course in the database.
    Returns: (success_bool, message_str)
    """
    course_id = course_id.strip()
    course_name = course_name.strip()
    enrollment_key = enrollment_key.strip()

    if not course_id or not course_name or not enrollment_key:
        return False, "Course ID, name, and enrollment key are required."

    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if course_id already exists
        cursor.execute("SELECT course_id FROM courses WHERE course_id = ?", (course_id,))
        if cursor.fetchone():
            conn.close()
            return False, "A course with this ID already exists."

        created_at = time.time()
        cursor.execute("""
            INSERT INTO courses (course_id, course_name, enrollment_key, description, topics, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (course_id, course_name, enrollment_key, description, topics, created_by, created_at))

        conn.commit()
        conn.close()
        return True, "Course created successfully!"
    except Exception as e:
        conn.close()
        return False, f"Failed to create course: {str(e)}"

def get_all_courses(db_path=DB_FILE):
    """
    Returns list of all courses as dicts.
    Each dict: {course_id, course_name, description, topics, created_by, created_at}
    NOTE: Do NOT return enrollment_key in this list (security)
    """
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT course_id, course_name, description, topics, created_by, created_at
            FROM courses
        """)
        rows = cursor.fetchall()
        conn.close()

        courses = []
        for row in rows:
            courses.append({
                "course_id": row[0],
                "course_name": row[1],
                "description": row[2],
                "topics": row[3],
                "created_by": row[4],
                "created_at": row[5]
            })
        return courses
    except Exception as e:
        print(f"Failed to fetch courses: {str(e)}")
        conn.close()
        return []

def get_course_by_id(course_id, db_path=DB_FILE):
    """
    Returns a single course dict including enrollment_key (for educator use).
    Returns None if not found.
    """
    course_id = course_id.strip()
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT course_id, course_name, enrollment_key, description, topics, created_by, created_at
            FROM courses WHERE course_id = ?
        """, (course_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "course_id": row[0],
                "course_name": row[1],
                "enrollment_key": row[2],
                "description": row[3],
                "topics": row[4],
                "created_by": row[5],
                "created_at": row[6]
            }
        return None
    except Exception as e:
        print(f"Failed to fetch course: {str(e)}")
        conn.close()
        return None

def enroll_in_course(username, course_id, enrollment_key, db_path=DB_FILE):
    """
    Enrolls a student in a course after validating the enrollment key.
    Returns: (success_bool, message_str)
    """
    username = username.strip().lower()
    course_id = course_id.strip()
    enrollment_key = enrollment_key.strip()

    if not username or not course_id or not enrollment_key:
        return False, "Username, course ID, and enrollment key are required."

    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Look up the course by course_id
        cursor.execute("SELECT enrollment_key FROM courses WHERE course_id = ?", (course_id,))
        course_row = cursor.fetchone()

        if not course_row:
            conn.close()
            return False, "Course not found."

        # 2. Verify enrollment_key matches
        if course_row[0] != enrollment_key:
            conn.close()
            return False, "Invalid enrollment key."

        # 3. Check if already enrolled
        cursor.execute("""
            SELECT username FROM enrollments WHERE username = ? AND course_id = ?
        """, (username, course_id))
        if cursor.fetchone():
            conn.close()
            return False, "You are already enrolled in this course."

        # 4. Insert into enrollments
        enrolled_at = time.time()
        cursor.execute("""
            INSERT INTO enrollments (username, course_id, enrolled_at)
            VALUES (?, ?, ?)
        """, (username, course_id, enrolled_at))

        conn.commit()
        conn.close()
        return True, "Successfully enrolled in the course!"
    except Exception as e:
        conn.close()
        return False, f"Enrollment failed: {str(e)}"

def get_student_courses(username, db_path=DB_FILE):
    """
    Returns list of course dicts that the student is enrolled in.
    Joins enrollments with courses table.
    Each dict: {course_id, course_name, description, topics, enrolled_at}
    """
    username = username.strip().lower()
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT c.course_id, c.course_name, c.description, c.topics, e.enrolled_at
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.username = ?
        """, (username,))
        rows = cursor.fetchall()
        conn.close()

        courses = []
        for row in rows:
            courses.append({
                "course_id": row[0],
                "course_name": row[1],
                "description": row[2],
                "topics": row[3],
                "enrolled_at": row[4]
            })
        return courses
    except Exception as e:
        print(f"Failed to fetch student courses: {str(e)}")
        conn.close()
        return []

def get_course_students(course_id, db_path=DB_FILE):
    """
    Returns list of usernames enrolled in a specific course.
    """
    course_id = course_id.strip()
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT username FROM enrollments WHERE course_id = ?
        """, (course_id,))
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]
    except Exception as e:
        print(f"Failed to fetch course students: {str(e)}")
        conn.close()
        return []
