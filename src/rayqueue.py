#!/usr/bin/env python

__author__  = 'Oliver Cordes'

__version__ = '0.0.1'

from app import create_app,db

from app.models import User, Project

# create an application
application = create_app()

app = application.app


# for flask shell command
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Project': Project}



# test this file
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4555, debug=True)
    #app.run(port=4555)
