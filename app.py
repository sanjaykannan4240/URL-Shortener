import os
import re
import secrets
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, redirect, render_template, request, g

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "shortener.db"))
CODE_LENGTH = 7
CODE_PATTERN = re.compile(r"^[A-Za-z0-9]{4,32}$")

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def get_db():
    if "db" not in g:
        database_path = Path(DATABASE)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL UNIQUE,
                original_url TEXT NOT NULL,
                clicks INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        db.commit()


def valid_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def create_code():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    db = get_db()
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(CODE_LENGTH))
        if db.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,)).fetchone() is None:
            return code


def serialize_url(row):
    short_url = request.host_url.rstrip("/") + "/" + row["short_code"]
    return {
        "id": row["id"],
        "short_code": row["short_code"],
        "short_url": short_url,
        "original_url": row["original_url"],
        "clicks": row["clicks"],
        "created_at": row["created_at"],
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/shorten")
def shorten_url():
    payload = request.get_json(silent=True) or request.form
    original_url = str(payload.get("url", "")).strip()
    custom_code = str(payload.get("custom_code", "")).strip()

    if not valid_url(original_url):
        return jsonify({"error": "Please enter a valid HTTP or HTTPS URL."}), 400
    if custom_code and not CODE_PATTERN.fullmatch(custom_code):
        return jsonify({"error": "Custom codes must be 4–32 letters or numbers."}), 400

    db = get_db()
    code = custom_code or create_code()
    try:
        cursor = db.execute(
            "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
            (code, original_url),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "That custom code is already in use."}), 409

    row = db.execute("SELECT * FROM urls WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(serialize_url(row)), 201


@app.get("/api/urls")
def list_urls():
    rows = get_db().execute("SELECT * FROM urls ORDER BY id DESC LIMIT 50").fetchall()
    return jsonify({"urls": [serialize_url(row) for row in rows]})


@app.get("/api/urls/<short_code>")
def get_url(short_code):
    row = get_db().execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    if row is None:
        return jsonify({"error": "Short URL not found."}), 404
    return jsonify(serialize_url(row))


@app.get("/<short_code>")
def redirect_short_url(short_code):
    if not CODE_PATTERN.fullmatch(short_code):
        return render_template("404.html"), 404
    db = get_db()
    row = db.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    if row is None:
        return render_template("404.html"), 404
    db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,))
    db.commit()
    return redirect(row["original_url"], code=302)


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
