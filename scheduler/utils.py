from typing import final
from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import jsonify

db = SQLAlchemy()


courses = {
    "COMP 10001": "Programming Fundamentals",
    "COMP 10062": "Programming in Java",
    "COMP 10065": "PHP & JavaScript",
    "COMP 10066": "Software Quality & Testing",
    "COMP 10204": "Programming in .NET",
    "COMP CO710": "HTML & CSS",
    "COMP CO859": "Database Theory",
}


def oauth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if (
                not identity["token"]
                or not identity["refresh_token"]
                or not identity["token_uri"]
                or not identity["client_id"]
                or not identity["client_secret"]
                or not identity["scopes"]
            ):
                raise Exception("Invalid identity in token.")
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return jsonify({"redirect": "/auth"})
        # if "credentials" not in session:
        #     return redirect(url_for("/.auth"))
        # return f(*args, **kwargs)

    return decorated_function