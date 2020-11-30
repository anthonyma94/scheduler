import logging
from scheduler.scraper import ScraperThread
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from scheduler.config import DevelopmentConfig, ProductionConfig
from scheduler.utils import db
from scheduler.appointment import Appointment
from dotenv import load_dotenv, find_dotenv


scraperThread = ScraperThread()
from scheduler.routes import bp

if find_dotenv() != "":
    load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
jwt = JWTManager(app)
CORS(app)

if app.config["ENV"].lower() == "development":
    app.config.from_object(DevelopmentConfig)
elif app.config["ENV"].lower() == "production":
    app.config.from_object(ProductionConfig)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.register_blueprint(bp)

with app.app_context():
    db.init_app(app)
    engine = db.get_engine()
    if not (Appointment.metadata.tables[Appointment.__tablename__].exists(engine)):
        db.create_all()
