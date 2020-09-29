from os import environ, urandom


class Config:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI")

    # for i in ["http://", "https://"]:
    #     if i in SERVER_NAME:
    #         SERVER_NAME = SERVER_NAME.replace(i, "")
    #         break


class DevelopmentConfig(Config):
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    SECRET_KEY = "wsuetrhigasdgfawergadfzcvbfgaldjrfhgaoisdufghp"
    # SERVER_NAME = "localhost:5000"


class ProductionConfig(Config):
    SECRET_KEY = urandom(32)
