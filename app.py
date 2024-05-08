from datetime import datetime
import json
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

import track

STUDY_TIME = 0

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('StudyBase.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        date DATE NOT NULL,
        duration_minutes INTEGER NOT NULL
    )
''')
# (Optional) Close the connection (good practice)
conn.commit()
conn.close()

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///StudyBase.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/account", methods=["GET", "POST"])
@track.login_required
def account(): 
    username = session["username"]
    return render_template("account.html", username=username)


@app.route("/about")
@track.login_required
def about(): 
    username = session["username"]
    return render_template("about.html", username=username)



@app.route("/password_change", methods=["GET", "POST"])
@track.login_required
def c_pass():

    if request.method == "GET":
        return render_template("password_change.html")
    else:
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("old_password")
        ):
            return render_template("password_change", error=True, message="Invalid username or password")

        hash_password = generate_password_hash(new_password)
        id = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash_password, id[0]['id'])

        return redirect("/")


@app.route("/delete")
@track.login_required
def delete(): 
    
    db.execute("DELETE FROM study_sessions WHERE username = (SELECT username from users WHERE id = ?)", session["user_id"])
    db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
    return redirect("/")

@app.route("/")
def index():    
    return render_template("login.html")


@app.route('/api/user_scores', methods=['GET'])
@track.login_required
def get_user_scores():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('StudyBase.db')
        cursor = conn.cursor()

        # Query to retrieve username and score data
        cursor.execute('SELECT username, duration_minutes FROM study_sessions')
        data = cursor.fetchall()

        # Close database connection
        conn.close()

        # Format data into a list of dictionaries
        user_scores = [{'username': row[0], 'score': row[1]} for row in data]

        # Return data as JSON response
        return jsonify(user_scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update', methods=['POST'])
@track.login_required
def update(): 
    
    date = datetime.now().date()
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    track.record_study_session(username[0]['username'], 25)
    return jsonify({'message': 'Focus time count updated successfully'})


@app.route("/home", methods = ["GET", "POST"])
@track.login_required
def home():
    username = session["username"]
    return render_template("home.html", username=username)


@app.route("/leaderboard")
@track.login_required
def leaderboard(): 
    username = session["username"]
    return render_template("leaderboard.html", username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted

        session["username"] = request.form.get("username")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", error=True,message="Invalid Username and/or Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@track.login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/records")
@track.login_required
def records(): 
    
    # Check if 'user_id' is present in the session
    if 'user_id' not in session:
        return "User ID not found in session"  # Handle if user_id is not in session

    # Connect to SQLite database
    conn = sqlite3.connect('StudyBase.db')
    cursor = conn.cursor()

    try:
        # Retrieve the username based on user_id from session (NOT recommended for security, use parameterized query)
        user_id = session['user_id']
        username_query = f"SELECT username FROM users WHERE id = {user_id}"
        cursor.execute(username_query)
        user_row = cursor.fetchone()

        if user_row:
            # Fetch records for the logged-in user
            records_query = f"SELECT date, duration_minutes FROM study_sessions WHERE username = (SELECT username FROM users WHERE id = {user_id})"
            cursor.execute(records_query)
            rows = cursor.fetchall()

            # Extract dates and quantities from rows
            dates = [row[0] for row in rows]
            quantities = [row[1] for row in rows]

            # Close cursor and connection
            cursor.close()
            conn.close()

            # Convert lists to JSON strings
            dates_json = json.dumps(dates)
            quantities_json = json.dumps(quantities)

            # Pass data to template for rendering
            username = session["username"]
            return render_template('records.html', dates=dates_json, quantities=quantities_json, username=username)

        else:
            return "User not found in database"  # Handle if user not found

    except Exception as e:
        # Handle any exceptions (e.g., database errors)
        return f"Error: {str(e)}"


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if password != confirm:
            return render_template("register.html", error=True, message="Passwords do not match")

        hashed_password = generate_password_hash(password)
        username = request.form.get("username")

        n = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(n) > 0:
            return render_template("register.html", error=True, message="Username already exists")

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)
        id = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = id[0]['id']
        track.record_study_session(username, 0)

        return redirect('/login')

    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)