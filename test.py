import regex, time, json
import requests
from lxml import html
from bs4 import BeautifulSoup
from scheduler.appointment import Appointment


# s = requests.Session()
# s.headers = headers
# s.post("https://mohawk2.mywconline.com/", data=login)
# res = s.post("https://mohawk2.mywconline.com/report_mlr.php", data=find_schedule)

# doc = html.fromstring(res.content)

# divs: html.Element = doc.xpath(
#     "//div[@class='content_form']//div[@class='form_frame']//div[@class='third_form_last']"
# )

# links = []
# for i in divs:
#     a = i[0][0].get("onclick")
#     match = regex.search(r"(?<=window\.open\(\')([^\']*)", a)
#     links.append("https://mohawk2.mywconline.com/" + match.group())

# if len(links) > 0:
#     appointments = []

#     for link in links:
#         res = s.get(link)

#         soup = BeautifulSoup(res.content, "html.parser")

#         appointment = Appointment.create(link, soup)

#         if appointment is not None:
#             appointments.append(appointment)

#     for i in appointments:
#         print(i)

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