#!/usr/bin/env python

"""
rayqueue.py

written by: 2019-01-20
changed by; 2019-05-04

"""

__author__  = 'Oliver Cordes'
__version__ = '0.0.12'


# used for the cli extension
import click
from flask.cli import AppGroup

# the defaults for the APP
from app import create_app, db, socketio, activity
from app.models import User, Project, File, Image

import logging

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
    return {'db': db, 'User': User, 'Project': Project,
            'File': File, 'Image': Image }


"""
utility_processor

the function defines some extra variables in the jinja2
environment for the templates, the context of the
current app status is used!
"""
@app.context_processor
def utility_processor():
    return { 'rq_version': __version__,
             'rq_copyright': '2019 by {}'.format(__author__),
             'activity': activity }



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
#if __name__ != '__main__':
if 'gunicorn' in app.config['SERVER_SOFTWARE']:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


# test this file
if __name__ == "__main__":
    #app.run(host='0.0.0.0',
    socketio.run(app,
            host='0.0.0.0',
            port=4555,
            debug=True,
            extra_files=['./app/api/openapi.yaml'])
    #app.run(port=4555)
