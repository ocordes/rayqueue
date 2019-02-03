from datetime import datetime

from flask import current_app, make_response, abort, jsonify

from flask_login import current_user, login_user, logout_user, login_required

#from app import db
from app.api import bp

from app.models import User

from time import time
import jwt
import six

JWT_ISSUER           = 'rayqueue.com'
JWT_LIFETIME_SECONDS = 60 * 60        # 1h


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

# Data to serve with our API
PEOPLE = {
    "Farrell": {
        "username": "dfarrel",
        "first_name": "Doug",
        "last_name": "Farrell",
        "timestamp": get_timestamp()
    },
    "Brockman": {
        "username": "kbrockman",
        "first_name": "Kent",
        "last_name": "Brockman",
        "timestamp": get_timestamp()
    },
    "Easter": {
        "username": "beaster",
        "first_name": "Bunny",
        "last_name": "Easter",
        "timestamp": get_timestamp()
    }
}

# Create a handler for our read (GET) people
# it is possible to mask this with the login_required decorator!
@login_required
def read():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        sorted list of people
    """
    # Create the list of people from our data
    return [PEOPLE[key] for key in sorted(PEOPLE.keys())]




#def login(user):
def login(user):
    """
    This function performs a user check via username/password
    :param user:    contains username and password
    :return:        200 on success + access_token
                    401 if checks were not successful
    """
    username = user.get("username", None)
    password = user.get("password", None)

    #print(username)
    #print(password)

    user_info = User.query.filter_by(username=username).first()
    if user_info is None or not user_info.check_password(password):
        abort(
                 401,
                 "Invalid username or password",
             )


    timestamp = time()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": username,
    }

    data = {
              "status": 200,
              "token": jwt.encode(
                            payload,
                            current_app.config['SECRET_KEY'],
                            algorithm='HS256').decode('utf-8')
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

    # # Does the person exist already?
    # if lname not in PEOPLE and lname is not None:
    #     PEOPLE[lname] = {
    #         "lname": lname,
    #         "fname": fname,
    #         "timestamp": get_timestamp(),
    #     }
    #     return make_response(
    #         "{lname} successfully created".format(lname=lname), 201
    #     )
    #
    # # Otherwise, they exist, that's an error
    # else:
    #     abort(
    #         406,
    #         "Peron with last name {lname} already exists".format(lname=lname),
    #     )


def get_secret(user, token_info) -> str:
    return '''
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    '''.format(user=user, token_info=token_info)


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)
