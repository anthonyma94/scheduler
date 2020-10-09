import datetime, logging, os
from flask import redirect, request
from flask.blueprints import Blueprint
from flask.json import jsonify
from flask.templating import render_template
from sqlalchemy import func, DateTime, cast
from typing import List
from werkzeug.exceptions import InternalServerError
from werkzeug.wrappers import Response
from scheduler.utils import oauth_required
from scheduler.appointment import Appointment
from scheduler.google_calendar import getCredentials, getAuthURL
from scheduler.utils import db

bp = Blueprint("/", __name__)
from scheduler import scraperThread


@bp.route("/")
@bp.route("/index.html")
@oauth_required
def index():
    models = None

    if "sqlite" in os.environ.get("DATABASE_URI"):
        models = Appointment.query.filter(
            func.DATETIME(Appointment.end) >= datetime.datetime.now()
        ).all()
    else:
        models = Appointment.query.filter(
            cast(Appointment.end, DateTime) >= datetime.datetime.now()
        ).all()
        logging.info(models[0].end)
        logging.info(datetime.datetime.now())

    appointments = []

    for model in models:
        appointments.append(model.toDict())

    return render_template(
        "index.html",
        appointments=appointments,
    )


@bp.route("/auth")
def auth():
    auth_url = getAuthURL()
    return redirect(auth_url, code=302)


@bp.route("/auth/callback")
def callback():

    url = request.url
    getCredentials(url)

    return redirect("/", 302)


@bp.route("/getappointments")
def getAppointments():
    # global scraperThread
    try:
        scraperThread.run()
        scraperThread.progress = 0
    except Exception as e:
        resp = Response(response=str(e), status=500)
        raise InternalServerError(response=resp)

    return ("", 200)


@bp.route("/progress", methods=["GET"])
def progress():
    progress = scraperThread.progress
    if progress >= 0:
        return jsonify(progress=scraperThread.progress), 200
    else:
        return jsonify(message="error"), 500


@bp.route("/appointment/<int:id>")
def appointment(id):
    model = Appointment.query.get(id)
    return render_template("appointment.html", appointment=model.toDict())


@bp.route("/add/<int:id>", methods=["GET", "POST"])
@oauth_required
def add(id):
    if id == 0:
        appointments: List[Appointment] = Appointment.query.filter(
            Appointment.start >= datetime.datetime.now()
        ).all()

        for i in appointments:
            i.add_event()

        return ("", 200)

    appointment: Appointment = Appointment.query.get(id)

    if not appointment.calendarEventExists:
        appointment.add_event()

    return ("", 204)


@bp.route("/delete/<int:id>")
@oauth_required
def delete(id):
    appointment: Appointment = Appointment.query.get(id)
    appointment.deleteEvent()

    db.session.delete(appointment)
    db.session.commit()

    return redirect("/", code=302)
