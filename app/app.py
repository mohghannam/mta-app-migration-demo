import os
import uuid
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "mtc-demo-secret")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "mtcdemo"),
        user=os.getenv("DB_USER", "mtcdemo"),
        password=os.getenv("DB_PASSWORD", "mtcdemo"),
    )

def init_db():
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    owner VARCHAR(100) NOT NULL,
                    status VARCHAR(30) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("SELECT COUNT(*) FROM tasks")
            if cur.fetchone()[0] == 0:
                cur.executemany(
                    "INSERT INTO tasks (title, owner, status) VALUES (%s, %s, %s)",
                    [
                        ("Migrate database", "Ahmed", "Complete"),
                        ("Validate persistent storage", "Mohamed", "In Progress"),
                        ("Test application", "Platform Team", "Pending"),
                        ("Production cutover", "Migration Team", "Pending"),
                    ],
                )
        conn.commit()
    finally:
        conn.close()

def db_ready():
    try:
        init_db()
        return True
    except Exception:
        return False

@app.route("/health")
def health():
    return ("OK", 200) if db_ready() else ("Database unavailable", 503)

@app.route("/")
def index():
    conn = db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id")
            tasks = cur.fetchall()
    finally:
        conn.close()

    uploads = sorted(
        [p.name for p in UPLOAD_DIR.iterdir() if p.is_file()]
    )
    return render_template("index.html", tasks=tasks, uploads=uploads)

@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    owner = request.form.get("owner", "").strip()
    if not title or not owner:
        flash("Title and owner are required.")
        return redirect(url_for("index"))

    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, owner, status) VALUES (%s, %s, %s)",
                (title, owner, "Pending"),
            )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("index"))

@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        flash("Choose a file first.")
        return redirect(url_for("index"))

    safe_name = Path(f.filename).name
    destination = UPLOAD_DIR / f"{uuid.uuid4().hex[:8]}-{safe_name}"
    f.save(destination)
    return redirect(url_for("index"))

@app.route("/uploads/<path:name>")
def uploaded_file(name):
    return send_from_directory(UPLOAD_DIR, name, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
