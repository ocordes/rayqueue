#!/usr/bin/env python

__author__  = 'Oliver Cordes'

__version__ = '0.0.1'

from app import app, db

from app.models import User

@app.app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


# test this file
if __name__ == "__main__":
    app.run(port=4555, debug=True)
    #app.run(port=4555)
