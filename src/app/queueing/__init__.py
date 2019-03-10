"""
app/queueing/__init__.py


written by: Oliver Cordes 2019-03-10
changed by: Oliver Cordes 2019-03-10

"""

from flask import Blueprint

bp = Blueprint('queueing', __name__)


from app.queueing import routes
from app.queueing.manager import Manager

queue_manager = Manager()
