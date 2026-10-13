from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():

    with sqlite3.connect("focus.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM sessions")

        rows = cursor.fetchall()

        cursor.execute("SELECT SUM(duration) AS total_duration FROM sessions")
        sum_row = cursor.fetchone()

        total_duration = sum_row["total_duration"] if sum_row["total_duration"] else 0
    
        return render_template("index.html", sessions=rows, total_duration=total_duration)

@app.route("/add", methods=["POST"])
def add_session():
    session_title = request.form.get("title")
    session_duration = request.form.get("duration")
    session_date = request.form.get("date")
    session_time = request.form.get("time")
    session_notes = request.form.get("notes")

    with sqlite3.connect("focus.db") as connection:
        cursor = connection.cursor()

        add_query = "INSERT INTO sessions (title, s_date, duration, notes) VALUES (?, ?, ?, ?)"
        
        cursor.execute(add_query, (session_title, session_date, session_duration, session_notes))
        connection.commit()

    return redirect(url_for('home'))
    #return f"Worked on {session_title} on this date: {session_date} at {session_time} for {session_duration}. Details: {session_notes}"


@app.route('/delete/<int:session_id>', methods=['POST'])
def delete_session(session_id):
    with sqlite3.connect("focus.db") as connection:
        cursor = connection.cursor()

        delete_query = "DELETE FROM sessions WHERE id = ?"

        cursor.execute(delete_query, (session_id,))
        connection.commit()

    return redirect(url_for('home'))