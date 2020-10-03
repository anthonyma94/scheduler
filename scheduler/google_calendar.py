import datetime
import logging
from os.path import abspath, dirname, join
from os import environ
from typing import List
import flask
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CLIENT_SECRET_FILE = "client_secret.json"
PATH = dirname(dirname(abspath(__file__)))
CAL_ID = environ.get("CAL_ID")


class CalendarEvent:
    def __init__(
        self,
        summary: str,
        description: str,
        start: datetime.datetime,
        end: datetime.datetime,
    ):
        self.summary = summary
        self.description = description
        self.start = start
        self.end = end

    def toDict(self):
        event = {
            "summary": self.summary,
            "description": self.description,
            "start": {
                "dateTime": self.start.replace(microsecond=0).isoformat(),
                "timeZone": "America/Toronto",
            },
            "end": {
                "dateTime": self.end.replace(microsecond=0).isoformat(),
                "timeZone": "America/Toronto",
            },
        }

        return event


def getAuthURL():
    flow = Flow.from_client_secrets_file(join(PATH, CLIENT_SECRET_FILE), scopes=SCOPES)

    flow.redirect_uri = environ.get("BASE_URL") + flask.url_for("/.callback")

    auth_url, state = flow.authorization_url(access_type="offline")

    flask.session["state"] = state

    return auth_url


def getCredentials(resp):
    state = flask.session["state"]
    flow = Flow.from_client_secrets_file(
        join(PATH, CLIENT_SECRET_FILE), scopes=SCOPES, state=state
    )

    flow.redirect_uri = environ.get("BASE_URL") + flask.url_for("/.callback")

    flow.fetch_token(authorization_response=resp)

    credentials = flow.credentials

    flask.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def addEvent(event: CalendarEvent) -> str:
    if "credentials" not in flask.session:
        logging.error("Missing credentials. Redirecting...")
        return flask.redirect("/auth", 303)

    cred = credentials.Credentials(**flask.session["credentials"])
    service = build("calendar", "v3", credentials=cred, cache_discovery=False)

    res = service.events().insert(calendarId=CAL_ID, body=event.toDict()).execute()

    logging.info("Event created: {0}".format(res.get("htmlLink")))

    return res.get("id")


def deleteEvent(id):
    if "credentials" not in flask.session:
        logging.error("Missing credentials. Redirecting...")
        return flask.redirect("/auth", 303)

    cred = credentials.Credentials(**flask.session["credentials"])

    service = build("calendar", "v3", credentials=cred, cache_discovery=False)

    res = service.events().delete(calendarId=CAL_ID, eventId=id).execute()

    if res is None:
        logging.info("Event deleted.")
    else:
        logging.error(res)
