import logging
from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from scheduler.config import DevelopmentConfig, ProductionConfig
from dotenv import load_dotenv, find_dotenv
from functools import wraps

courses = {
    "COMP 10001": "Programming Fundamentals",
    "COMP 10062": "Programming in Java",
    "COMP 10065": "PHP & JavaScript",
    "COMP 10066": "Software Quality & Testing",
    "COMP 10204": "Programming in .NET",
    "COMP CO710": "HTML & CSS",
    "COMP CO859": "Database Theory",
}

if find_dotenv() != "":
    load_dotenv(find_dotenv())


app = Flask(__name__)

if app.config["ENV"].lower() == "development":
    app.config.from_object(DevelopmentConfig)
elif app.config["ENV"].lower() == "production":
    app.config.from_object(ProductionConfig)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


def oauth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "credentials" not in session:
            return redirect(url_for("auth"))
        return f(*args, **kwargs)

    return decorated_function


db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

from scheduler.appointment import Appointment

engine = db.get_engine()
if not (Appointment.metadata.tables[Appointment.__tablename__].exists(engine)):
    db.create_all()