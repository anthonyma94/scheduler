from os import environ, urandom


class Config:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI")


class DevelopmentConfig(Config):
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    SECRET_KEY = "wsuetrhigasdgsdfgjhdgfhjhldjrfhgaoisdufghp"


class ProductionConfig(Config):
    SECRET_KEY = urandom(32)
