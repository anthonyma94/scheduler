import os, regex, datetime, logging, sys, requests, json
from threading import Thread
from bs4 import BeautifulSoup
from lxml import html
from werkzeug.exceptions import InternalServerError
from scheduler.appointment import Appointment
from scheduler.utils import db
from sqlalchemy.exc import IntegrityError


def scrape():
    headers = None
    find_schedule = None
    login = None
    with open("scheduler/static/config.json") as f:
        data = json.load(f)
        headers, find_schedule, login = (
            data["headers"],
            data["find_schedule"],
            data["login"],
        )

    login["username"], login["password"] = (
        os.environ["USERNAME"],
        os.environ["PASSWORD"],
    )
    find_schedule["sdate"], find_schedule["edate"] = (
        datetime.date.today().strftime("%B %d, %Y"),
        (datetime.date.today() + datetime.timedelta(days=21)).strftime("%B %d, %Y"),
    )

    s = requests.Session()
    s.headers = headers
    s.post("https://mohawk2.mywconline.com/", data=login)
    res = s.post("https://mohawk2.mywconline.com/report_mlr.php", data=find_schedule)

    doc = html.fromstring(res.content)

    divs: html.Element = doc.xpath(
        "//div[@class='content_form']//div[@class='form_frame']//div[@class='third_form_last']"
    )

    links = []
    for i in divs:
        a = i[0][0].get("onclick")
        match = regex.search(r"(?<=window\.open\(\')([^\']*)", a)
        links.append("https://mohawk2.mywconline.com/" + match.group())

    appointments = []
    if len(links) > 0:
        for link in links:
            res = s.get(link)

            soup = BeautifulSoup(res.content, "html.parser")

            appointment = Appointment.create(link, soup)

            if appointment is not None:
                appointments.append(appointment)
        logging.info(f"Found {len(appointments)} active appointments.")
    else:
        logging.info("Found 0 appointments.")

    return appointments


def parse(appointments):
    if len(appointments) > 0:
        logging.info(f"Adding {len(appointments)} appointments to database...")

        """
        Checks if there are any cancelled events.
        It checks appointments in DB against grabbed appointments and removes if it isn't in the list.
        """
        appointmentsComp = []
        dbComp = []
        cancelledAppointments = []

        for i in appointments:
            item = {"name": i.name, "start": i.start, "end": i.end}
            appointmentsComp.append(item)

        appointmentsInDB = Appointment.query.filter(
            Appointment.start >= datetime.date.today()
        ).all()

        for i in appointmentsInDB:
            item = {"name": i.name, "start": i.start, "end": i.end}
            dbComp.append(item)

        for i in range(len(dbComp)):
            if not (dbComp[i] in appointmentsComp):
                cancelledAppointments.append(appointmentsInDB[i])

        # Add appointments to db
        for appointment in appointments:
            db.session.add(appointment)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                db.session.flush()

        if len(cancelledAppointments) > 0:
            logging.info(
                f"Found {len(cancelledAppointments)} cancelled appointments. Removing from database..."
            )
            # Remove cancelled appointments from db
            for appointment in cancelledAppointments:
                appointment.deleteEvent()

                db.session.delete(appointment)

            db.session.commit()
            logging.info(f"Removed {len(cancelledAppointments)} from database.")
        logging.info(f"Added {len(appointments)} to database.")
    else:
        logging.info("No appointments to parse. Continuing...")


class ScraperThread(Thread):
    def __init__(self):
        self.progress = 0
        super().__init__()

    def run(self) -> None:
        try:
            self.progress = 10
            # raise Exception
            logging.info("Starting scraper...")
            appointments = scrape()
            self.progress = 50
            parse(appointments)
            logging.info("Finished. Exiting scraper...")
            self.progress = 100
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            self.progress = -1
            logging.error(
                f"{exception_type.__name__} at line {exception_traceback.tb_lineno} in {filename}: {e}"
            )
            raise InternalServerError(description="An unknown error occured.")
