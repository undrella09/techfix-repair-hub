import re
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


def email_is_valid(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()
        if user is None:
            session.clear()
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped_view


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = get_current_user()
            if user is None:
                session.clear()
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if user.role not in roles:
                return render_template("403.html"), 403
            return view(*args, **kwargs)
        return wrapped_view
    return decorator


@auth_bp.app_context_processor
def inject_current_user():
    return {"current_user": get_current_user()}


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user() is not None:
        return redirect(
            url_for(
                "admin.dashboard"
                if get_current_user().role == "admin"
                else "customer.dashboard"
            )
        )

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        errors = []

        if not name:
            errors.append("Full name is required.")
        elif len(name) > 120:
            errors.append("Full name must be 120 characters or fewer.")

        if not email:
            errors.append("Email is required.")
        elif not email_is_valid(email):
            errors.append("Please enter a valid email address.")
        elif User.query.filter_by(email=email).first():
            errors.append("Email is already registered.")

        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", name=name, email=email)

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="customer",
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user() is not None:
        current = get_current_user()
        return redirect(
            url_for("admin.dashboard" if current.role == "admin" else "customer.dashboard")
        )

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user.id
        session["role"] = user.role

        flash(f"Welcome back, {user.name}!", "success")
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("customer.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
