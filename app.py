from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "attendance_secret_key_2024"

DB_PATH = os.path.join(os.path.dirname(__file__), "attendance.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    today = date.today().isoformat()
    conn = get_db()
    records = conn.execute(
        "SELECT * FROM attendance WHERE date = ? ORDER BY time DESC", (today,)
    ).fetchall()
    conn.close()
    return render_template("index.html", records=records, today=today)


@app.route("/mark", methods=["POST"])
def mark_attendance():
    name = request.form.get("name", "").strip()
    status = request.form.get("status", "Present")

    if not name:
        flash("Please enter a name.", "error")
        return redirect(url_for("index"))

    if status not in ("Present", "Absent"):
        status = "Present"

    now = datetime.now()
    today = now.date().isoformat()
    current_time = now.strftime("%H:%M:%S")

    conn = get_db()
    # Prevent duplicate for same person on same day
    existing = conn.execute(
        "SELECT id FROM attendance WHERE name = ? AND date = ?", (name, today)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE attendance SET status = ?, time = ? WHERE id = ?",
            (status, current_time, existing["id"]),
        )
        flash(f"Updated attendance for {name} to {status}.", "success")
    else:
        conn.execute(
            "INSERT INTO attendance (name, status, date, time) VALUES (?, ?, ?, ?)",
            (name, status, today, current_time),
        )
        flash(f"Attendance marked for {name} as {status}.", "success")

    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/history")
def history():
    conn = get_db()
    records = conn.execute(
        "SELECT * FROM attendance ORDER BY date DESC, time DESC"
    ).fetchall()
    conn.close()
    return render_template("history.html", records=records)


@app.route("/api/today")
def api_today():
    today = date.today().isoformat()
    conn = get_db()
    records = conn.execute(
        "SELECT name, status, time FROM attendance WHERE date = ? ORDER BY time DESC",
        (today,),
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in records])


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = get_db()
    conn.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    flash("Record deleted.", "success")
    return redirect(request.referrer or url_for("index"))

# Create database table when the app starts
init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
