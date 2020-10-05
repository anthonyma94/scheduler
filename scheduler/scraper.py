import os, regex, datetime, logging, sys
from threading import Thread
from bs4 import BeautifulSoup
from typing import List, Match
from selenium.webdriver import Remote
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from werkzeug.exceptions import InternalServerError
from scheduler.appointment import Appointment
from scheduler.utils import db
from sqlalchemy.exc import IntegrityError

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement


class ScraperThread(Thread):
    def __init__(self):
        self.progress = 0
        super().__init__()

    def run(self) -> None:
        logging.info("Running")
        browser = None
        try:
            logging.info("Starting scraper...")
            opts = Options()
            opts.headless = True

            try:
                browser = Remote("http://192.168.20.15:4444/wd/hub", options=opts)
                self.progress = 5
            except Exception as e:
                logging.error(e)
                self.progress = -1
                raise InternalServerError(
                    description="Browser instance creation failed."
                )

            logging.info("Browser instance created.")
            self.progress = 20

            username = os.environ["USERNAME"]
            pw = os.environ["PASSWORD"]

            logging.info("Navigating to website...")
            browser.get("https://mohawk2.mywconline.com/")
            # Initial login if it exists
            try:
                submit: WebElement = browser.find_element_by_name("login")

                name: WebElement = browser.find_element_by_name("username")
                password: WebElement = browser.find_element_by_name("password")

                name.send_keys(username)
                password.send_keys(pw)

                submit.click()

            except NoSuchElementException as e:
                logging.info("Already logged in. Continuing...")

            # Navigate to Master Listings Report
            logging.info("Navigating to Master List...")
            if self is not None:
                self.progress += 20
            select = Select(browser.find_element_by_id("dynamic_select"))

            for option in select.options:
                match = regex.search(r"Course Peer Tutors", option.text)
                if match:
                    select.select_by_value(option.get_attribute("value"))
                    break

            div: WebElement = browser.find_element_by_class_name("header_bar_lower")
            link: WebElement = div.find_element_by_xpath(
                "//*[@alt='Master Listings Report']"
            ).find_element_by_xpath("./..")
            path = link.get_attribute("href")
            browser.get(path)

            # Find appointments in Master Listings
            logging.info("Finding appointments...")
            if self is not None:
                self.progress += 20
            tutor = Select(browser.find_element_by_name("rid"))

            for option in tutor.options:
                match = regex.search(r"Anthony M", option.text)
                if match:
                    tutor.select_by_value(option.get_attribute("value"))
                    break

            start = datetime.date.today()
            startDateInput: WebElement = browser.find_element_by_id("repdate1")
            startDateInput.clear()
            startDateInput.send_keys(start.strftime("%B %d, %Y"))
            end = start + datetime.timedelta(days=21)
            endDateInput = browser.find_element_by_id("repdate2")
            endDateInput.clear()
            endDateInput.send_keys(end.strftime("%B %d, %Y"))

            submit = browser.find_element_by_name("submit")
            submit.click()

            # Sort appointments
            parent: WebElement = browser.find_element_by_class_name("form_frame")
            divs: List[WebElement] = browser.find_elements_by_xpath(
                "//div[@class='content_form']//div[@class='form_frame']//div[@class='third_form_last']"
            )

            links = []

            for link in divs:
                a: WebElement = link.find_element_by_tag_name("a")

                match: Match = regex.search(
                    r"(?<=window\.open\(\')([^\']*)", str(a.get_attribute("onclick"))
                )
                links.append("https://mohawk2.mywconline.com/" + match.group())

            if len(links) > 0:
                appointments = []

                for link in links:
                    browser.get(link)

                    soup = BeautifulSoup(browser.page_source, "lxml")

                    appointment = Appointment.create(link, soup)

                    if appointment is not None:
                        appointments.append(appointment)

                if self is not None:
                    self.progress += 20
                if len(appointments) > 0:
                    logging.info(
                        f"Found {len(appointments)} appointments. Adding to database..."
                    )

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
                        Appointment.start >= start
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
                        # Remove cancelled appointments from db
                        for appointment in cancelledAppointments:
                            appointment.deleteEvent()

                            db.session.delete(appointment)

                        db.session.commit()
            else:
                logging.info("Found 0 appointments.")

            logging.info("Finished. Exiting scraper...")
            self.progress += 20
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            self.progress = -1
            logging.error(
                f"{exception_type.__name__} at line {exception_traceback.tb_lineno} in {filename}: {e}"
            )
            raise InternalServerError
        finally:
            if browser is not None:
                browser.quit()
