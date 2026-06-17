import sqlite3
import json
import os
from datetime import datetime

# Check if running on Vercel
IS_VERCEL = os.environ.get("VERCEL") == "1"

ORIGINAL_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "scheme_ai.db")

if IS_VERCEL:
    DB_PATH = "/tmp/scheme_ai.db"
    # Copy from original read-only location to /tmp on startup if it doesn't exist
    if not os.path.exists(DB_PATH) and os.path.exists(ORIGINAL_DB_PATH):
        import shutil
        shutil.copyfile(ORIGINAL_DB_PATH, DB_PATH)
else:
    DB_PATH = ORIGINAL_DB_PATH

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # User Profile Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User_Profile (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        income REAL NOT NULL,
        occupation TEXT NOT NULL,
        education_level TEXT NOT NULL,
        state TEXT NOT NULL,
        social_category TEXT NOT NULL,
        disability_status BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    
    # Scheme Details Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Scheme_Details (
        scheme_id TEXT PRIMARY KEY,
        scheme_name TEXT NOT NULL,
        category TEXT NOT NULL,
        benefits TEXT NOT NULL,
        description TEXT NOT NULL,
        eligibility_criteria TEXT NOT NULL, -- JSON string storing age, income, caste, state, occupation limits
        required_documents TEXT NOT NULL,    -- JSON string array
        application_process TEXT NOT NULL,   -- JSON string array
        official_portal TEXT NOT NULL
    )
    """)
    
    # Recommendation Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Recommendation (
        recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        scheme_id TEXT NOT NULL,
        eligibility_score REAL NOT NULL,
        recommendation_rank INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User_Profile(user_id),
        FOREIGN KEY (scheme_id) REFERENCES Scheme_Details(scheme_id)
    )
    """)
    
    # Query History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Query_History (
        query_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_query TEXT NOT NULL,
        assistant_response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User_Profile(user_id)
    )
    """)
    
    # Scheme Updates Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Scheme_Updates (
        update_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id TEXT NOT NULL,
        update_type TEXT NOT NULL,
        update_description TEXT NOT NULL,
        update_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scheme_id) REFERENCES Scheme_Details(scheme_id)
    )
    """)
    
    conn.commit()
    conn.close()

# User operations
def save_user_profile(age: int, gender: str, income: float, occupation: str, 
                       education_level: str, state: str, social_category: str, 
                       disability_status: bool) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO User_Profile (age, gender, income, occupation, education_level, state, social_category, disability_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (age, gender, income, occupation, education_level, state, social_category, 1 if disability_status else 0))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_profile(user_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM User_Profile WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

# Scheme operations
def upsert_scheme(scheme_id: str, scheme_name: str, category: str, benefits: str, 
                  description: str, eligibility_criteria: dict, 
                  required_documents: list, application_process: list, 
                  official_portal: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO Scheme_Details (scheme_id, scheme_name, category, benefits, description, eligibility_criteria, required_documents, application_process, official_portal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(scheme_id) DO UPDATE SET
        scheme_name=excluded.scheme_name,
        category=excluded.category,
        benefits=excluded.benefits,
        description=excluded.description,
        eligibility_criteria=excluded.eligibility_criteria,
        required_documents=excluded.required_documents,
        application_process=excluded.application_process,
        official_portal=excluded.official_portal
    """, (
        scheme_id,
        scheme_name,
        category,
        benefits,
        description,
        json.dumps(eligibility_criteria),
        json.dumps(required_documents),
        json.dumps(application_process),
        official_portal
    ))
    conn.commit()
    conn.close()

def get_all_schemes():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM Scheme_Details").fetchall()
    conn.close()
    schemes = []
    for row in rows:
        scheme = dict(row)
        scheme["eligibility_criteria"] = json.loads(scheme["eligibility_criteria"])
        scheme["required_documents"] = json.loads(scheme["required_documents"])
        scheme["application_process"] = json.loads(scheme["application_process"])
        schemes.append(scheme)
    return schemes

def get_scheme_by_id(scheme_id: str):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM Scheme_Details WHERE scheme_id = ?", (scheme_id,)).fetchone()
    conn.close()
    if row:
        scheme = dict(row)
        scheme["eligibility_criteria"] = json.loads(scheme["eligibility_criteria"])
        scheme["required_documents"] = json.loads(scheme["required_documents"])
        scheme["application_process"] = json.loads(scheme["application_process"])
        return scheme
    return None

# Recommendation operations
def save_recommendations(user_id: int, recommendations: list):
    """recommendations is a list of tuples: (scheme_id, eligibility_score, rank)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete old recommendations for this user first
    cursor.execute("DELETE FROM Recommendation WHERE user_id = ?", (user_id,))
    
    for scheme_id, score, rank in recommendations:
        cursor.execute("""
        INSERT INTO Recommendation (user_id, scheme_id, eligibility_score, recommendation_rank)
        VALUES (?, ?, ?, ?)
        """, (user_id, scheme_id, score, rank))
    conn.commit()
    conn.close()

def get_user_recommendations(user_id: int):
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT r.scheme_id, r.eligibility_score, r.recommendation_rank, r.timestamp,
           s.scheme_name, s.category, s.benefits, s.description, s.official_portal
    FROM Recommendation r
    JOIN Scheme_Details s ON r.scheme_id = s.scheme_id
    WHERE r.user_id = ?
    ORDER BY r.recommendation_rank ASC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Chat History operations
def save_query_history(user_id: int, query: str, response: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO Query_History (user_id, user_query, assistant_response)
    VALUES (?, ?, ?)
    """, (user_id, query, response))
    conn.commit()
    conn.close()

def get_chat_history(user_id: int, limit: int = 10):
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT user_query, assistant_response, timestamp
    FROM Query_History
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    # Return in chronological order
    return [dict(row) for row in reversed(rows)]
