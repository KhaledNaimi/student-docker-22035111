-- ============================================================
--  Student Data Management System — Database Initialisation
--  Automatically executed by MySQL on first container start
-- ============================================================

CREATE DATABASE IF NOT EXISTS studentdb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE studentdb;

-- ── TABLE 1: students ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    student_id      INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    first_name      VARCHAR(80)     NOT NULL,
    last_name       VARCHAR(80)     NOT NULL,
    national_id     VARCHAR(20)     NOT NULL UNIQUE,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    date_of_birth   DATE            NOT NULL,
    gender          ENUM('Male','Female','Other') NOT NULL,
    department      VARCHAR(100)    NOT NULL,
    enrollment_date DATE            NOT NULL DEFAULT (CURDATE()),
    gpa             DECIMAL(4,2)    DEFAULT 0.00,
    status          ENUM('Active','Graduated','Suspended') NOT NULL DEFAULT 'Active',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── TABLE 2: courses ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    course_id       INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    course_code     VARCHAR(20)     NOT NULL UNIQUE,
    course_name     VARCHAR(150)    NOT NULL,
    credit_hours    TINYINT UNSIGNED NOT NULL,
    instructor_name VARCHAR(120)    NOT NULL,
    department      VARCHAR(100)    NOT NULL,
    semester        ENUM('Fall','Spring','Summer') NOT NULL,
    academic_year   YEAR            NOT NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── TABLE 3: enrollments (junction) ───────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id   INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    student_id      INT UNSIGNED    NOT NULL,
    course_id       INT UNSIGNED    NOT NULL,
    grade           DECIMAL(5,2)    DEFAULT NULL,
    letter_grade    ENUM('A','B','C','D','F','Incomplete') DEFAULT NULL,
    enrolled_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (enrollment_id),
    UNIQUE KEY uq_student_course (student_id, course_id),
    CONSTRAINT fk_enroll_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_enroll_course  FOREIGN KEY (course_id)
        REFERENCES courses(course_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  SEED DATA
-- ============================================================

-- 5 courses
INSERT INTO courses (course_code, course_name, credit_hours, instructor_name, department, semester, academic_year) VALUES
('CS101', 'Introduction to Computer Science',  3, 'Dr. Ahmad Khalil',   'Computer Science',    'Fall',   2025),
('CS201', 'Data Structures & Algorithms',       3, 'Dr. Layla Hassan',   'Computer Science',    'Fall',   2025),
('CS301', 'Database Systems',                   3, 'Dr. Omar Nasser',    'Computer Science',    'Spring', 2025),
('MATH101','Calculus I',                        4, 'Dr. Sara Mansour',   'Mathematics',         'Fall',   2025),
('NET201', 'Computer Networks',                 3, 'Dr. Rami Issa',      'Network Engineering', 'Spring', 2025);

-- 10 students
INSERT INTO students (first_name, last_name, national_id, email, date_of_birth, gender, department, enrollment_date, gpa, status) VALUES
('Mohammed', 'Al-Rashid',  'JO20010101', 'mohammed.rashid@uni.edu',   '2001-03-15', 'Male',   'Computer Science',    '2023-09-01', 3.75, 'Active'),
('Sara',     'Khalil',     'JO20010202', 'sara.khalil@uni.edu',       '2001-07-22', 'Female', 'Computer Science',    '2023-09-01', 3.90, 'Active'),
('Omar',     'Hassan',     'JO20000303', 'omar.hassan@uni.edu',       '2000-11-08', 'Male',   'Mathematics',         '2022-09-01', 3.20, 'Active'),
('Fatima',   'Nasser',     'JO20010404', 'fatima.nasser@uni.edu',     '2001-01-30', 'Female', 'Network Engineering', '2023-09-01', 3.60, 'Active'),
('Khalid',   'Mansour',    'JO19990505', 'khalid.mansour@uni.edu',    '1999-05-14', 'Male',   'Computer Science',    '2021-09-01', 2.85, 'Active'),
('Rania',    'Saleh',      'JO20020606', 'rania.saleh@uni.edu',       '2002-08-19', 'Female', 'Mathematics',         '2024-09-01', 3.95, 'Active'),
('Bilal',    'Kareem',     'JO20010707', 'bilal.kareem@uni.edu',      '2001-12-03', 'Male',   'Network Engineering', '2023-09-01', 3.10, 'Active'),
('Noor',     'Aqel',       'JO20000808', 'noor.aqel@uni.edu',         '2000-04-25', 'Female', 'Computer Science',    '2022-09-01', 3.45, 'Graduated'),
('Tariq',    'Obeid',      'JO19980909', 'tariq.obeid@uni.edu',       '1998-09-11', 'Male',   'Mathematics',         '2020-09-01', 2.30, 'Suspended'),
('Lina',     'Farhat',     'JO20021010', 'lina.farhat@uni.edu',       '2002-06-07', 'Female', 'Computer Science',    '2024-09-01', 3.80, 'Active');

-- 15 enrollments
INSERT INTO enrollments (student_id, course_id, grade, letter_grade) VALUES
(1, 1, 88.00, 'B'), (1, 2, 92.00, 'A'), (1, 4, 78.00, 'C'),
(2, 1, 95.00, 'A'), (2, 3, 91.00, 'A'),
(3, 4, 72.00, 'C'), (3, 5, 68.00, 'D'),
(4, 5, 85.00, 'B'), (4, 1, 80.00, 'B'),
(5, 2, 74.00, 'C'), (5, 3, NULL,  NULL),
(6, 4, 99.00, 'A'), (6, 1, 97.00, 'A'),
(7, 5, 82.00, 'B'),
(10,1, NULL,  NULL);
