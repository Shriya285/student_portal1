import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from datetime import datetime

# Database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shriya@123",
            database="student_management_system"
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def authenticate_user(user_id, password):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user and user['password'] == hash_password(password):
            return user
        return None
    finally:
        cursor.close()
        conn.close()

# User creation
def create_user(user_id, password, role, name, email, semester=None, branch=None, section=None):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)

        # Insert into users table
        cursor.execute("""
            INSERT INTO users (user_id, password, role, name, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, hashed_password, role, name, email))

        # If the role is 'student', insert into the students table
        if role == 'student':
            cursor.execute("""
                INSERT INTO students (srn, semester, branch, section)
                VALUES (%s, %s, %s, %s)
            """, (user_id, semester, branch, section))

        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Admin Dashboard
def show_admin_dashboard():
    st.header("Admin Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Register User", "Manage Users", "View Enrollments"])
    
    with tab1:
        register_user()
    
    with tab2:
        manage_users()
    
    with tab3:
        view_enrollments()

# Register User
def register_user():
    st.subheader("Register New User")
    role = st.selectbox("Role", ["Student", "Faculty", "Admin"], key="register_user_role")
    name = st.text_input("Name", key="register_user_name")
    email = st.text_input("Email", key="register_user_email")
    user_id = st.text_input("User ID", key="register_user_id")
    password = st.text_input("Password", type="password", key="register_user_password")

    # If the role is 'student', ask for additional details
    semester = branch = section = None
    if role == "Student":
        semester = st.number_input("Semester", min_value=1, max_value=8, step=1, key="register_user_semester")
        branch = st.text_input("Branch", key="register_user_branch")
        section = st.text_input("Section", key="register_user_section")

    if st.button("Register User", key="register_user_button"):
        if create_user(user_id, password, role.lower(), name, email, semester, branch, section):
            st.success("User registered successfully!")
        else:
            st.error("Failed to register user.")

def manage_users():
    st.subheader("Manage Users")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, role, name, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    st.table(users)

def view_enrollments():
    st.subheader("View Enrollments")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.srn, u.name, c.course_name, s.semester, s.branch, s.section
        FROM student_courses sc
        JOIN students s ON sc.srn = s.srn
        JOIN users u ON s.srn = u.user_id
        JOIN courses c ON sc.course_id = c.course_id
    """)
    enrollments = cursor.fetchall()
    cursor.close()
    conn.close()

    st.table(enrollments)

# Student Dashboard
def show_student_dashboard():
    st.header("Student Dashboard")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Courses", "Timetable", "Assignments", "Course Materials", "Chat"])
    
    with tab1:
        show_enrolled_courses()
    
    with tab2:
        show_timetable()
    
    with tab3:
        show_assignments()
    
    with tab4:
        show_course_materials()
    
    with tab5:
        show_chat()

def show_enrolled_courses():
    st.subheader("Enrolled Courses")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.course_name, u.name as faculty_name
        FROM student_courses sc
        JOIN courses c ON sc.course_id = c.course_id
        JOIN users u ON c.faculty_id = u.user_id
        WHERE sc.srn = %s
    """, (st.session_state.user['user_id'],))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    st.table(courses)

def show_timetable():
    st.subheader("Timetable")
    st.write("Embed Google Calendar here")
    st.components.v1.iframe("https://calendar.google.com/calendar/embed?src=your_calendar_id", height=600)

def show_assignments():
    st.subheader("Assignments")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.title, a.description, a.deadline, c.course_name
        FROM assignments a
        JOIN courses c ON a.course_id = c.course_id
        JOIN student_courses sc ON c.course_id = sc.course_id
        WHERE sc.srn = %s
    """, (st.session_state.user['user_id'],))
    assignments = cursor.fetchall()
    cursor.close()
    conn.close()

    st.table(assignments)

def show_course_materials():
    st.subheader("Course Materials")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT cm.title, cm.file_path, c.course_name, cm.upload_date
        FROM course_materials cm
        JOIN courses c ON cm.course_id = c.course_id
        JOIN student_courses sc ON c.course_id = sc.course_id
        WHERE sc.srn = %s
    """, (st.session_state.user['user_id'],))
    materials = cursor.fetchall()
    cursor.close()
    conn.close()

    for idx, material in enumerate(materials):
        st.write(f"**{material['title']}** - {material['course_name']}")
        st.write(f"Uploaded on: {material['upload_date']}")
        st.download_button(
            label="Download",
            data=open(material['file_path'], 'rb').read(),
            file_name=material['file_path'].split('/')[-1],
            mime="application/octet-stream",
            key=f"download_material_{idx}"
        )

def show_chat():
    st.subheader("Chat Forum")
    st.write("Chat functionality to be implemented")

# Faculty Dashboard
def show_faculty_dashboard():
    st.header("Faculty Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Upload Material", "Upload Assignment", "View Students", "Chat"])
    
    with tab1:
        upload_course_material()
    
    with tab2:
        upload_assignment()
    
    with tab3:
        view_enrolled_students()
    
    with tab4:
        show_chat()

def upload_course_material():
    st.subheader("Upload Course Material")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_id, course_name FROM courses WHERE faculty_id = %s", (st.session_state.user['user_id'],))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    course = st.selectbox("Select Course", options=courses, format_func=lambda x: x['course_name'], key="upload_material_course")
    title = st.text_input("Material Title", key="upload_material_title")
    file = st.file_uploader("Choose a file", type=["pdf", "docx", "pptx"], key="upload_material_file")

    if file and title and st.button("Upload", key="upload_material_button"):
        file_path = f"course_materials/{course['course_id']}_{file.name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO course_materials (course_id, title, file_path, upload_date)
            VALUES (%s, %s, %s, %s)
        """, (course['course_id'], title, file_path, datetime.now()))
        conn.commit()

        cursor.close()
        conn.close()

        st.success("Material uploaded successfully!")

def upload_assignment():
    st.subheader("Upload Assignment")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_id, course_name FROM courses WHERE faculty_id = %s", (st.session_state.user['user_id'],))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    course = st.selectbox("Select Course", options=courses, format_func=lambda x: x['course_name'], key="upload_assignment_course")
    title = st.text_input("Assignment Title")
    description = st.text_area("Assignment Description")
    deadline = st.date_input("Deadline")
    file = st.file_uploader("Choose a file (optional)", type=["pdf", "docx"])

    if title and description and deadline and st.button("Upload",key="upload_assignment_button"):
        file_path = None
        if file:
            file_path = f"assignments/{course['course_id']}_{file.name}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assignments (course_id, title, description, deadline, file_path)
            VALUES (%s, %s, %s, %s, %s)
        """, (course['course_id'], title, description, deadline, file_path))
        
        # Create notifications for students
        cursor.execute("""
            INSERT INTO notifications (user_id, message)
            SELECT sc.srn, %s
            FROM student_courses sc
            WHERE sc.course_id = %s
        """, (f"New assignment '{title}' has been uploaded for {course['course_name']}. Deadline: {deadline}", course['course_id']))
        
        conn.commit()
        cursor.close()
        conn.close()

        st.success("Assignment uploaded successfully!")
def view_enrolled_students():
    st.subheader("Enrolled Students")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.course_name, u.name, s.srn, s.semester, s.branch, s.section
        FROM courses c
        JOIN student_courses sc ON c.course_id = sc.course_id
        JOIN students s ON sc.srn = s.srn
        JOIN users u ON s.srn = u.user_id
        WHERE c.faculty_id = %s
    """, (st.session_state.user['user_id'],))
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    st.table(students)

# Main app
def main():
    st.set_page_config(page_title="Student Management System", layout="wide")

    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        show_login_page()
    else:
        show_dashboard()

def show_login_page():
    st.title("Student Management System")
    role = st.selectbox("Select your role:", ["Admin", "Student", "Faculty"])
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(user_id, password)
        if user and user['role'].lower() == role.lower():
            st.session_state.user = user
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials or role mismatch.")

def show_dashboard():
    user = st.session_state.user
    st.title(f"Welcome, {user['name']}!")

    if user['role'] == 'admin':
        show_admin_dashboard()
    elif user['role'] == 'student':
        show_student_dashboard()
    elif user['role'] == 'faculty':
        show_faculty_dashboard()

    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()