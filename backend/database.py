import psycopg2
import psycopg2.extras
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Support both DATABASE_URL (Render) and individual variables (local)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render provides a full connection URL
    import urllib.parse

    result = urllib.parse.urlparse(DATABASE_URL)
    DB_CONFIG = {
        "host": result.hostname,
        "database": result.path[1:],
        "user": result.username,
        "password": result.password,
        "port": result.port or 5432,
    }
else:
    # Local development
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "medisimplify"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "port": os.getenv("DB_PORT", "5432"),
    }


def get_connection():
    """Create and return a database connection"""
    return psycopg2.connect(**DB_CONFIG)


def create_tables():
    """
    Create reports table if it doesn't exist.
    Why: We need somewhere to store all patient reports.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            raw_text TEXT,
            simplified_text TEXT,
            risk_level TEXT,
            abnormal_values JSONB,
            action_plan TEXT,
            disclaimer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables created successfully!")


def save_report(
    filename: str,
    file_type: str,
    raw_text: str,
    simplified_text: str,
    risk_level: str,
    abnormal_values: list,
    action_plan: str,
    disclaimer: str,
) -> str:
    """
    Save a new report to the database.
    Returns the report ID.
    """
    import json

    conn = get_connection()
    cursor = conn.cursor()

    report_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO reports (
            id, filename, file_type, raw_text,
            simplified_text, risk_level, abnormal_values,
            action_plan, disclaimer
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            report_id,
            filename,
            file_type,
            raw_text,
            simplified_text,
            risk_level,
            json.dumps(abnormal_values),
            action_plan,
            disclaimer,
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()
    return report_id


def get_all_reports() -> list:
    """Get all reports for history page"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT id, filename, file_type, risk_level, 
               simplified_text, action_plan, created_at
        FROM reports
        ORDER BY created_at DESC
    """)

    reports = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in reports]


def get_report_by_id(report_id: str) -> dict:
    """Get a single report by ID"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        """
        SELECT * FROM reports WHERE id = %s
    """,
        (report_id,),
    )

    report = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(report) if report else None


def delete_report(report_id: str) -> bool:
    """Delete a report by ID"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM reports WHERE id = %s
    """,
        (report_id,),
    )

    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return deleted
