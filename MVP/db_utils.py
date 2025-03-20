import psycopg2
from psycopg2.extras import DictCursor
import os
from database import get_connection

def create_user(full_name: str, email: str, role: str = 'student'):
    """
    Inserts a user into the 'users' table.
    Returns the newly created user_id.
    """
    query = """
        INSERT INTO users (full_name, email, role)
        VALUES (%s, %s, %s)
        RETURNING user_id;
    """
    conn = None
    user_id = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, (full_name, email, role))
        user_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        print("Error creating user:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return user_id

def create_exam(title: str, course_code: str, created_by: int):
    """
    Inserts an exam row into 'exams'.
    Returns the new exam_id.
    """
    query = """
        INSERT INTO exams (title, course_code, created_by)
        VALUES (%s, %s, %s)
        RETURNING exam_id;
    """
    conn = None
    exam_id = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, (title, course_code, created_by))
        exam_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        print("Error creating exam:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return exam_id

def create_exam_session(exam_id: int, student_id: int):
    """
    Inserts a new exam session row.
    Returns the session_id.
    """
    query = """
        INSERT INTO exam_sessions (exam_id, student_id)
        VALUES (%s, %s)
        RETURNING session_id;
    """
    conn = None
    session_id = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, (exam_id, student_id))
        session_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        print("Error creating exam session:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return session_id

def flag_suspicious_event(session_id: int, event_type: str, confidence: float = None):
    """
    Inserts a new suspicious event for a given exam session.
    """
    query = """
        INSERT INTO suspicious_events (session_id, event_type, confidence)
        VALUES (%s, %s, %s)
        RETURNING event_id;
    """
    conn = None
    event_id = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, (session_id, event_type, confidence))
        event_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        print("Error inserting suspicious event:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return event_id

def complete_exam_session(session_id: int):
    """
    Marks an exam session as completed and sets end_time to NOW().
    """
    query = """
        UPDATE exam_sessions
        SET end_time = NOW(),
            status = 'completed'
        WHERE session_id = %s;
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, (session_id,))
        conn.commit()
    except Exception as e:
        print("Error completing exam session:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_exam_session_details(session_id: int):
    """
    Retrieves exam session info, including suspicious events.
    """
    query = """
        SELECT es.session_id,
               es.exam_id,
               es.student_id,
               es.start_time,
               es.end_time,
               es.status,
               se.event_id,
               se.event_type,
               se.confidence,
               se.detected_at
        FROM exam_sessions es
        LEFT JOIN suspicious_events se
        ON es.session_id = se.session_id
        WHERE es.session_id = %s;
    """
    conn = None
    results = []
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(query, (session_id,))
        rows = cur.fetchall()
        for row in rows:
            results.append(dict(row))
    except Exception as e:
        print("Error fetching exam session details:", e)
    finally:
        if conn:
            conn.close()
    return results
