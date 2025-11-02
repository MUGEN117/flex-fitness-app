from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ------------------------
# Trainer Login
# ------------------------
@auth_bp.route("/login-trainer", methods=["GET", "POST"])
def login_trainer():
    if current_user.is_authenticated and current_user.role == "trainer":
        return redirect(url_for("trainer.dashboard_trainer"))

    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        user = User.query.filter_by(email=email, role="trainer").first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # 🔑 Flask-Login manages the session for you
            flash("Welcome back, Trainer!", "success")
            return redirect(url_for("trainer.dashboard_trainer"))

        flash("Invalid email or password.", "danger")

    return render_template("login-trainer.html")


# ------------------------
# Member Login
# ------------------------
@auth_bp.route("/login-member", methods=["GET", "POST"])
def login_member():
    if current_user.is_authenticated and current_user.role == "member":
        return redirect(url_for("member.dashboard"))

    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        user = User.query.filter_by(email=email, role="member").first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("member.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login-member.html")


# ------------------------
# Register
# ------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "warning")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(password)
        username = request.form.get("username") or email.split("@")[0]

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role=role,
        )

        if user.role == "trainer":
            user.generate_trainer_code()

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login_trainer" if role == "trainer" else "auth.login_member"))

    return render_template("create-account.html")


# ------------------------
# Logout
# ------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()  # 🔑 Logs out cleanly
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
