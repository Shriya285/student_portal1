-- Create the database
CREATE DATABASE IF NOT EXISTS student_management_system;
USE student_management_system;

-- Users table
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student', 'faculty') NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Students table
CREATE TABLE students (
    srn VARCHAR(50) PRIMARY KEY,
    semester INT NOT NULL,
    branch VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    FOREIGN KEY (srn) REFERENCES users(user_id)
);

-- Courses table
CREATE TABLE courses (
    course_id VARCHAR(20) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    faculty_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (faculty_id) REFERENCES users(user_id)
);


-- Student_Courses table (for enrollment)
CREATE TABLE student_courses (
    srn VARCHAR(50),
    course_id VARCHAR(20),
    PRIMARY KEY (srn, course_id),
    FOREIGN KEY (srn) REFERENCES students(srn),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Course_Materials table
CREATE TABLE course_materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Assignments table
CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    deadline DATETIME NOT NULL,
    file_path VARCHAR(255),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Notifications table
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Chat_Messages table
CREATE TABLE chat_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id VARCHAR(50) NOT NULL,
    receiver_id VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);
INSERT INTO users (user_id, password, role, name, email)
VALUES('ADMIN001',SHA2('admin123',256),'admin','Admin','admin@gmail.com');
INSERT INTO users (user_id, password, role, name, email)
VALUES 
('admin1', SHA2('password123', 256), 'admin', 'John Doe', 'john.doe@example.com'),
('admin2', SHA2('securepass456', 256), 'admin', 'Jane Smith', 'jane.smith@example.com'),
('admin3', SHA2('adminpass789', 256), 'admin', 'Bob Johnson', 'bob.johnson@example.com');

INSERT INTO courses (course_id, course_name, faculty_id)
VALUES
('UE22CS351A', 'Database Management System', 'FACULTY1');