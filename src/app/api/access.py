""""

app/api/users.py

written by: Oliver Cordes 2019-01-26
changed by: Oliver Cordes 2019-05-18

"""


from datetime import datetime

from flask import current_app, make_response, abort, jsonify

from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.exceptions import Unauthorized

from app import db
from app.api import bp

from app.models import User, HostInfo

from time import time
import jwt

JWT_ISSUER           = 'rayqueue.com'
JWT_LIFETIME_SECONDS = 60 * 60        # 1h
#JWT_LIFETIME_SECONDS = 10


# taken from example the decode function

def decode_token(token):
    try:
        return jwt.decode(token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256'])

    except jwt.exceptions.InvalidTokenError as e:
        abort( 401, e.__str__(), )

    except:
        abort( 401,
                'Token not valid!',
            )



# login
def login(user):
    """
    This function performs a user check via username/password
    :param user:    contains username and password
    :return:        200 on success + access_token
                    401 if checks were not successful
    """
    username = user.get('username', None)
    password = user.get('password', None)
    client_version = user.get('client_version', None)


    # check if username/password combination is valid
    user_info = User.query.filter_by(username=username).first()
    if user_info is None or not user_info.check_password(password):
        abort(
                 401,
                 "Invalid username or password",
             )


    # create an access token
    timestamp = time()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": user_info.id,
    }

    # return the response payload
    data = {
              "status": 200,
              "token": jwt.encode(
                            payload,
                            current_app.config['SECRET_KEY'],
                            algorithm='HS256').decode('utf-8')
    }

    resp = jsonify(data)
    resp.status_code = 200


    current_app.logger.info('API-Login: User {} successfully logged in (client_version={})'.format(user_info.username, client_version))

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


def get_secret2(user, token_info) -> str:
    return '''
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    '''.format(user=user, token_info=token_info)


"""
host_info

register the host info dataset in database and returns the id

:param user:        the user id of the login user
:param token_info:  the token
:param body:        the dataset with the hostinfo
:rvalue:            the id of the hostinfo in database
"""
def host_info(user, token_info, body):
    info = HostInfo.get_hostinfo(body)
    if info is None:
        abort(404, 'Cannot create hostinfo from data')

    db.session.add(info)
    db.session.commit()

    return jsonify({'hostid': info.id})
