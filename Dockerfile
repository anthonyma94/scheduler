FROM python:3.8 as builder

COPY requirements.txt .

ENV PATH=/root/.local/bin:$PATH

RUN pip install --user -r requirements.txt
RUN pip install gunicorn

# FROM python:3.8-slim

# WORKDIR /app
# COPY --from=builder /root/.local /root/.local

COPY main.py client_secret.json ./
COPY scheduler/ ./scheduler
# RUN chmod +x boot.sh

# ENV PATH=/root/.local:$PATH
ENV FLASK_ENV=production
ENV FLASK_APP=main.py
ENV CAL_ID=bjvsi3rukjf409j1l7ue4vtt7o@group.calendar.google.com
ENV HA_URL=http://docker.anthonyma.ca:8123
ENV BASE_URL=https://scheduler.anthonyma.ca

CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "main:app"]