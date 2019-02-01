from datetime import datetime

from flask import make_response, abort

from flask_login import current_user, login_user, logout_user, login_required



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



def login(user):
    """
    This function performs a login via username/password
    into the system
    :param user:    contains username and password
    :return:        201 on success, 401 on person exists
    """
    username = user.get("username", None)
    pwssword = user.get("password", None)


    user_info = User.query.filter_by(username=username).first()
    if user_info is None or not user_info.check_password(password):
        abort(
                 401,
                 "Invalid username or password",
             )

    return make_response(
        "{username} successfully logged in".format(username=username), 201 )

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
