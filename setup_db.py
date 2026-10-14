import sqlite3

with sqlite3.connect("focus.db") as connection:
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            s_date DATE NOT NULL, 
            duration INTEGER NOT NULL,
            notes TEXT NOT NULL
            )
    """)