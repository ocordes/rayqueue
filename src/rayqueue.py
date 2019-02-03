#!/usr/bin/env python

__author__  = 'Oliver Cordes'

__version__ = '0.0.1'

from app import create_app,db

from app.models import User

# create an application
app = create_app()


# for flask shell command
@app.app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}



# test this file
if __name__ == "__main__":
    app.run(port=4555, debug=True)
    #app.run(port=4555)
