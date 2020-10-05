import time, datetime, pytz
from scheduler.scraper import ScraperThread
from threading import Thread


unaware = datetime.datetime(2020, 10, 5, 9, 0, 0)
aware = pytz.timezone("America/Toronto").localize(unaware).astimezone(pytz.utc)

print(unaware)
print(datetime.datetime.utcnow())
print(aware)
print(unaware >= datetime.datetime.now())