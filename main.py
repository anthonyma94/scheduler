import datetime
from sqlalchemy import func
from typing import List
from flask import redirect, request
from scheduler import app, db, oauth_required
from scheduler.appointment import Appointment
from scheduler.scraper import scraper
from flask.templating import render_template
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import atexit, json
from scheduler.google_calendar import getCredentials, getAuthURL


@app.route("/")
@app.route("/index.html")
@oauth_required
def index():

    models = Appointment.query.filter(
        func.DATE(Appointment.start) >= datetime.date.today()
    ).all()

    appointments = []

    for model in models:
        appointments.append(model.toDict())

    appointmentsJSON = json.dumps(appointments)

    return render_template(
        "index.html",
        appointments=appointments,
        appointmentsJSON=appointmentsJSON,
    )


@app.route("/auth")
def auth():
    auth_url = getAuthURL()
    return redirect(auth_url, code=302)


@app.route("/auth/callback")
def callback():

    url = request.url
    getCredentials(url)

    return redirect("/", 302)


@app.route("/getappointments")
def getAppointments():
    scraper()

    return ("", 200)


@app.route("/appointment/<int:id>")
def appointment(id):
    model = Appointment.query.get(id)
    return render_template("appointment.html", appointment=model.toDict())


@app.route("/add/<int:id>", methods=["GET", "POST"])
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


@app.route("/delete/<int:id>")
@oauth_required
def delete(id):
    appointment: Appointment = Appointment.query.get(id)
    appointment.deleteEvent()

    db.session.delete(appointment)
    db.session.commit()

    return redirect("/", code=302)


if __name__ == "__main__":
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(
    #     func=scraper, trigger="cron", minute=15, hour=17, day_of_week="0-4"
    # )
    # scheduler.add_job(
    #     func=Appointment.create_all_events,
    #     trigger="cron",
    #     minute=20,
    #     hour=17,
    #     day_of_week="0-4",
    # )
    # scheduler.start()
    # atexit.register(lambda: scheduler.shutdown())

    if app.config["ENV"] == "development":
        app.run(host="0.0.0.0")
    else:
        app.run()
