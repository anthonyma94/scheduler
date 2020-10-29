import datetime, json, os, string, logging
from flask.helpers import url_for
from scheduler.utils import db, courses
import scheduler.google_calendar as google
from bs4 import BeautifulSoup


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, unique=True, nullable=False)
    end = db.Column(db.DateTime, unique=True, nullable=False)
    name = db.Column(db.String(60), nullable=False)
    link = db.Column(db.String(100), nullable=False, unique=True)
    course = db.Column(db.String(40), nullable=False)
    comments = db.Column(db.String(5000), nullable=False)
    esl = db.Column(db.Boolean, nullable=False)
    cal_id = db.Column(db.String(100))

    @property
    def calendarEventExists(self):
        return self.cal_id is not None and self.cal_id != ""

    @staticmethod
    def create(link: str, soup: BeautifulSoup):

        # Find name
        nameSpan: BeautifulSoup = soup.p.span
        name = nameSpan.get_text().strip()
        name = string.capwords(name)

        # Check if placeholder
        placeholderSpan = soup.find(attrs={"class": "half_last"}).p

        placeholder = "PLACEHOLDER" in str(placeholderSpan)
        if placeholder and name == "Anthony Ma":
            return

        # Find start and end time
        timeSpan: BeautifulSoup = soup.find(attrs={"class": "half_first"}).p.span

        date = timeSpan.contents[0].strip()
        times = timeSpan.contents[2].strip()

        times = timeSpan.contents[2].strip().split(" to ")
        start = datetime.datetime.strptime(
            f"{date} {times[0]}", "%A, %B %d, %Y %I:%M%p"
        )
        end = datetime.datetime.strptime(f"{date} {times[1]}", "%A, %B %d, %Y %I:%M%p")

        # Find name
        nameSpan: BeautifulSoup = soup.p.span
        name = nameSpan.get_text().strip()
        name = string.capwords(name)

        # Find comments
        commentsSpan = soup.find(
            "b", text="Please state what you want to work on in the tutoring session"
        ).findNext("span")
        comments = commentsSpan.get_text().strip()

        # Find course
        courseSpan = soup.find("b", text="Selected Focus").findNext("span")
        course = courseSpan.get_text().strip()
        if course is None or course == "":
            course = "N/A"

        # Find esl
        eslSpan = soup.find("b", text="Is English your second language?").findNext(
            "span"
        )
        eslText = eslSpan.get_text().strip()
        esl = "YES" in eslText.upper()

        return Appointment(
            start=start,
            end=end,
            name=name,
            link=link,
            course=course,
            esl=esl,
            comments=comments,
        )

    def add_event(self):
        logging.info("Adding event...")
        if self.calendarEventExists:
            logging.error("Event already added.")
            return

        event = google.CalendarEvent(
            summary="Tutoring session",
            description="<a href='{0}' target='_blank'>Appointment</a>".format(
                os.environ.get("BASE_URL") + url_for("/.appointment", id=self.id)
            ),
            start=self.start,
            end=self.end,
        )

        id = google.addEvent(event)
        self.cal_id = id
        db.session.commit()

    def deleteEvent(self):
        if self.cal_id == "" or self.cal_id is None:
            logging.info("Appointment has not been added to calendar.")
            return

        google.deleteEvent(self.cal_id)
        return

    def toDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sort": self.start.replace(tzinfo=datetime.timezone.utc).timestamp(),
            "start": datetime.datetime.strftime(self.start, "%a, %b %d %I:%M %p"),
            "end": datetime.datetime.strftime(self.end, "%a, %b %d %I:%M %p"),
            "course": f"{courses[self.course]} ({self.course})"
            if self.course in courses
            else self.course,
            "esl": "Yes" if self.esl else "No",
            "comments": self.comments,
            "link": self.link,
            "added": self.calendarEventExists,
        }

    def isSame(self, other) -> bool:
        return (
            self.start == other.start
            and self.end == other.end
            and self.name == other.name
        )

    def __repr__(self) -> str:
        obj = {
            "id": self.id,
            "name": self.name,
            "start": str(self.start),
            "end": str(self.end),
        }
        return json.dumps(obj)