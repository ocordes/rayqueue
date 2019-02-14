"""

api/checks.py

written by: Oliver Cordes 2019-02-14
changed by: Oliver Cordes 2019-02-14

"""

from flask import current_app, make_response, abort, jsonify


"""
body_get

checks if an element is in a json-body which is a
python dictonary, if key is not present raise a
404 error

:param body:  the json body
:param key:   the key we re looking for
:rvalue:      the value of key
"""
def body_get(body, key):
    if key in body.keys():
        value = body.get(key)
        return value
    else:
        abort( 400,
                'No {} given'.format(key)
                )
