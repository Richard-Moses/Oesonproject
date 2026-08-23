"""
Church Security Album
----------------------
A simple Flask + SQLite app for storing and visually verifying church members.

Run it with:
    python app.py

Then open http://127.0.0.1:5000 in your browser.

ACCESS CONTROL:
The whole app sits behind a single shared password (a login gate) since
it holds real members' names, phone numbers, and photos. The default
password is "changeme123" — change it before sharing the app with
anyone, either by editing APP_PASSWORD below or by setting the
CHURCH_APP_PASSWORD environment variable.
"""

import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PHOTO_FOLDER = os.path.join(BASE_DIR, "uploads", "photos")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

APP_PASSWORD = os.environ.get("CHURCH_APP_PASSWORD", "changeme123")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "church.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = PHOTO_FOLDER
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

db = SQLAlchemy(app)


# ---------------------------------------------------------------------
# Database Model
# ---------------------------------------------------------------------
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    group = db.Column(db.String(20), nullable=False, default="Men")
    phone = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(200), nullable=False)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Runs on import (not just "python app.py"), so the photo folder and
# database table also get created under a WSGI server like PythonAnywhere,
# where __main__ never executes.
os.makedirs(PHOTO_FOLDER, exist_ok=True)
with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------
# Access control — one shared password gates every page and every photo.
# The static folder (CSS/JS/icons/manifest) stays public so the login
# page itself can be styled and installed as a PWA before signing in.
# ---------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password", "") == APP_PASSWORD:
            session["authenticated"] = True
            next_path = request.form.get("next") or url_for("index")
            return redirect(next_path)
        error = "Incorrect password."
    return render_template("login.html", error=error, next=request.args.get("next", ""))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------
@app.route("/sw.js")
def service_worker():
    # Served from the site root (not /static/) so its default scope is "/"
    # and it can control every page, per the Service Worker spec.
    return send_from_directory(BASE_DIR, "sw.js", mimetype="application/javascript")


@app.route("/photos/<path:filename>")
@login_required
def member_photo(filename):
    # Photos live outside static/ specifically so they are never reachable
    # without logging in first.
    return send_from_directory(PHOTO_FOLDER, filename)


@app.route("/")
@login_required
def index():
    members = Member.query.order_by(Member.full_name.asc()).all()
    return render_template("index.html", members=members, total=len(members))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_member():
    error = None

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        member_id = request.form.get("member_id", "").strip()
        group = request.form.get("group", "Men")
        phone = request.form.get("phone", "").strip()
        photo_file = request.files.get("photo")

        if not full_name or not member_id:
            error = "Full name and Member ID are required."
        elif not photo_file or photo_file.filename == "":
            error = "A photo is required."
        elif not allowed_file(photo_file.filename):
            error = "Photo must be an image file (png, jpg, jpeg, gif, webp)."
        elif Member.query.filter_by(member_id=member_id).first():
            error = f"Member ID '{member_id}' is already in use."
        else:
            filename = secure_filename(f"{member_id}_{photo_file.filename}")
            photo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            new_member = Member(
                full_name=full_name,
                member_id=member_id,
                group=group,
                phone=phone,
                photo=filename,
            )
            db.session.add(new_member)
            db.session.commit()
            return redirect(url_for("index"))

    return render_template("add_member.html", error=error)


# ---------------------------------------------------------------------
# App startup
# ---------------------------------------------------------------------
if __name__ == "__main__":
    if APP_PASSWORD == "changeme123":
        print("!! Using the default password 'changeme123' — set CHURCH_APP_PASSWORD to change it.")
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", debug=debug_mode)
