from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_session():
    session_title = request.form.get("title")
    session_duration = request.form.get("duration")
    session_date = request.form.get("date")
    session_time = request.form.get("time")
    session_notes = request.form.get("notes")

    with sqlite3.connect("focus.db") as connection:
        cursor = connection.cursor()

        add_query = "INSERT INTO sessions (title, duration) VALUES (?, ?)"
        
        cursor.execute(add_query, (session_title, session_duration))
        connection.commit()

    return "Success!"
    # return f"Worked on {session_title} on {session_date} at {session_time} for {session_duration}. Details: {session_notes}"