from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('MY_SECRET_KEY')

fillWidth = 0

@app.route("/")
def home():

    target_hours = 100

    with sqlite3.connect("focus.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM sessions")

        rows = cursor.fetchall()

        cursor.execute("SELECT SUM(duration) AS total_duration FROM sessions")
        sum_row = cursor.fetchone()

        total_duration = sum_row["total_duration"] if sum_row["total_duration"] else 0

        today_date = datetime.now().strftime("%H:%M")
        cursor.execute("SELECT SUM(duration) AS daily_total_duration FROM sessions WHERE s_date = ?", (today_date,))
        daily_sum_row= cursor.fetchone()


        total_daily_duration = daily_sum_row["daily_total_duration"] if daily_sum_row["daily_total_duration"] else 0

        # calculated hours / inputted hours
        # c/i * 100
        
        if target_hours and total_daily_duration:
            fillWidth = target_hours / total_daily_duration * 100
        else:
            fillWidth = 0
    
        return render_template("index.html", sessions=rows, total_duration=total_duration, widthValue=fillWidth)

@app.route("/add", methods=["POST"])
def add_session():
    session_title = request.form.get("title")
    session_duration = request.form.get("duration")
    session_date = request.form.get("date")
    session_time = request.form.get("time")
    session_notes = request.form.get("notes")

    # if session_duration == "":

    if session_date == "":
        session_date = date.today().isoformat()

    if session_time == "":
        now = datetime.now()
        session_time = now.strftime("%H:%M")

    with sqlite3.connect("focus.db") as connection:
        cursor = connection.cursor()

        add_query = "INSERT INTO sessions (title, s_date, duration, notes) VALUES (?, ?, ?, ?)"
        
        cursor.execute(add_query, (session_title, session_date, session_duration, session_notes))
        connection.commit()

    flash("Session added successfully", "success")
    return redirect(url_for('home'))
    #return f"Worked on {session_title} on this date: {session_date} at {session_time} for {session_duration}. Details: {session_notes}"


@app.route('/delete/<int:session_id>', methods=['POST'])
def delete_session(session_id):
    with sqlite3.connect("focus.db") as connection:
        cursor = connection.cursor()

        delete_query = "DELETE FROM sessions WHERE id = ?"

        cursor.execute(delete_query, (session_id,))
        connection.commit()

    flash("Session deleted sucessfully", "error")
    return redirect(url_for('home'))

@app.route('/study/add', methods=['POST'])
def add_goal():
    pass