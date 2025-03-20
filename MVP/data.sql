-- 1. Create "users" table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,         -- e.g., 'student', 'teacher', 'admin'
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Create "exams" table
CREATE TABLE IF NOT EXISTS exams (
    exam_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    course_code VARCHAR(50) NOT NULL,  -- e.g., 'BIO101'
    created_by INTEGER NOT NULL,       -- references user_id of teacher
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_exam_creator
        FOREIGN KEY(created_by) 
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- 3. Create "exam_sessions" table
CREATE TABLE IF NOT EXISTS exam_sessions (
    session_id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP,                -- can be NULL until the session ends
    status VARCHAR(50) DEFAULT 'active', -- e.g., 'active', 'completed'
    CONSTRAINT fk_exam_sessions_exam
        FOREIGN KEY(exam_id)
        REFERENCES exams(exam_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_exam_sessions_student
        FOREIGN KEY(student_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- 4. (Optional) Create "suspicious_events" table
CREATE TABLE IF NOT EXISTS suspicious_events (
    event_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    event_type VARCHAR(100) NOT NULL,   -- e.g., 'MULTIPLE_FACES_DETECTED'
    confidence NUMERIC(5, 2),           -- e.g., 0.95
    detected_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_suspicious_session
        FOREIGN KEY(session_id)
        REFERENCES exam_sessions(session_id)
        ON DELETE CASCADE
);
