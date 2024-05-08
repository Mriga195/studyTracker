from functools import wraps
import sqlite3
from datetime import datetime

from flask import redirect, session

def record_study_session(username, duration_minutes):
    conn = sqlite3.connect('StudyBase.db')
    cursor = conn.cursor()

    # Get the current date
    current_date = datetime.now().date()

    cursor.execute("SELECT * FROM study_sessions WHERE username = ? AND date = ?", (username, current_date))
    existing_row = cursor.fetchone()

    # Insert a new study session record
    if existing_row:
        cursor.execute("UPDATE study_sessions SET duration_minutes = duration_minutes + 25 WHERE username = ? AND date = ?", (username, current_date))
    else:
        cursor.execute('''
            INSERT INTO study_sessions (username, date, duration_minutes)
            VALUES (?, ?, ?)
        ''', (username, current_date, duration_minutes))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
