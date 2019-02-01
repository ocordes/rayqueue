from datetime import datetime

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
