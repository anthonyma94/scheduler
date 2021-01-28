import regex, time, json
import requests
from lxml import html
from bs4 import BeautifulSoup
from scheduler.appointment import Appointment
from scheduler.scraper import ScraperThread


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

scraper = ScraperThread()

scraper.run()
