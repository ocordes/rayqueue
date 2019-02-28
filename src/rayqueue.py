#!/usr/bin/env python

__author__  = 'Oliver Cordes'

__version__ = '0.0.1'

# used for the cli extension
import click
from flask.cli import AppGroup

# the defaults for the APP
from app import create_app,db
from app.models import User, Project


# create an application
application = create_app()
app = application.app


"""
make_shell_context

the function provides default variables in the flask shell
environment
"""
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Project': Project}


"""
utility_processor

the function defines some extra variables in the jinja2
environment for the templates, the context of the
current app status is used!
"""
@app.context_processor
def utility_processor():
    return { 'rq_version': __version__,
             'rq_copyright': '2019 by {}'.format(__author__)}



# here are the definitions for the CLI extensions
user_cli = AppGroup('app')
"""

"""
@user_cli.command('check')
@click.argument('action')
def check_app(action):
    print(action)

app.cli.add_command(check_app)


# some specials for the gunicorn logger used in production
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


# test this file
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4555, debug=True)
    #app.run(port=4555)
