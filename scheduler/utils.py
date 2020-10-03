from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import redirect, url_for, session

db = SQLAlchemy()


courses = {
    "COMP 10001": "Programming Fundamentals",
    "COMP 10062": "Programming in Java",
    "COMP 10065": "PHP & JavaScript",
    "COMP 10066": "Software Quality & Testing",
    "COMP 10204": "Programming in .NET",
    "COMP CO710": "HTML & CSS",
    "COMP CO859": "Database Theory",
}


def oauth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "credentials" not in session:
            return redirect(url_for("/.auth"))
        return f(*args, **kwargs)

    return decorated_function