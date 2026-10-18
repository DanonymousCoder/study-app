from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('MY_SECRET_KEY')

fillDailyWidth = 0
fillWeeklyWidth = 0

@app.route("/")
def home():

    weekly_data = {}

    for i in range(6, -1, -1):
        date_string = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        weekly_data[date_string] = 0

    with sqlite3.connect("focus.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM sessions")

        rows = cursor.fetchall()

        cursor.execute("SELECT SUM(duration) AS total_duration FROM sessions")
        sum_row = cursor.fetchone()

        total_duration = sum_row["total_duration"] if sum_row["total_duration"] else 0

        today_date = date.today().isoformat()
        cursor.execute("SELECT SUM(duration) AS daily_total_duration FROM sessions WHERE s_date = ?", (today_date,))
        daily_sum_row= cursor.fetchone()

        seven_days_ago = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(duration) AS weekly_total_duration FROM sessions WHERE s_date >= ?", (seven_days_ago,))
        weekly_sum_row = cursor.fetchone()

        total_daily_duration = daily_sum_row["daily_total_duration"] if daily_sum_row["daily_total_duration"] else 0

        total_weekly_duration = weekly_sum_row["weekly_total_duration"] if weekly_sum_row["weekly_total_duration"] else 0

        # fetch_target_hours_query = "SELECT daily_goal FROM study_goal"
        cursor.execute("SELECT daily_goal FROM study_goal")
        target_daily_hours = cursor.fetchone()[0]

        cursor.execute("SELECT weekly_goal FROM study_goal")
        target_weekly_hours = cursor.fetchone()[0]


        cursor.execute("SELECT s_date, SUM(duration) AS total_day_duration FROM sessions WHERE s_date >= ? GROUP BY s_date ORDER BY s_date ASC", (seven_days_ago,))
        raw_chart_data = cursor.fetchall()

        # calculated hours / inputted hours
        # c/i * 100
        
        if target_daily_hours and total_daily_duration:
            fillDailyWidth = (total_daily_duration / target_daily_hours) * 100
        else:
            fillDailyWidth = 0

        if target_weekly_hours and total_weekly_duration:
            fillWeeklyWidth = (total_weekly_duration / target_weekly_hours) * 100
        else:
            fillWeeklyWidth = 0

        for row in cursor.fetchall():
            db_date = row[0]
            db_duration = row[1]

            if db_date in weekly_data:
                weekly_data[db_date] = db_duration

        chart_dates = [datetime.strptime(date_str, "%Y-%m-%d").strftime("%a") for date_str in  weekly_data.keys()]
        chart_durations = list(weekly_data.values())
        
        return render_template("index.html", sessions=rows, total_duration=total_duration, dailyWidthValue=fillDailyWidth, weeklyWidthValue=fillWeeklyWidth, chart_dates=chart_dates, chart_durations=chart_durations)


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

@app.route('/set_goal', methods=['POST'])
def set_goal():
    type_of_goal = request.form.get("goal-duration")
    goal_value = request.form.get("goal-number")

    with sqlite3.connect("focus.db") as connection:
        cursor = connection.cursor()

        if type_of_goal == "daily":
            add_query = "UPDATE study_goal SET daily_goal = ? WHERE id = 1"
        else:
            add_query = "UPDATE study_goal SET weekly_goal = ? WHERE id = 1"

        cursor.execute(add_query, (goal_value,))
    return redirect(request.referrer or url_for("home"))

@app.route("/edit/<int:session_id>", methods=["POST"])
def edit_session(session_id):
    session_title = request.form.get("title")
    session_duration = request.form.get("duration")
    session_date = request.form.get("date")
    session_time = request.form.get("time")
    session_notes = request.form.get("notes")

    if session_date == "":
        session_date = date.today().isoformat()
    
    if session_time == "":
        now = datetime.now()
        session_time = now.strftime("%H:%M")

        with sqlite3.connect("focus.db") as connection:
            cursor = connection.cursor()

            add_query = "UPDATE  sessions SET title = ?, duration = ?, s_date = ?, notes = ?  WHERE id = ?"
            cursor.execute(add_query, (session_title, session_duration, session_date, session_notes, session_id))

    return redirect(url_for("home"))