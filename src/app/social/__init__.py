from flask import Blueprint

bp = Blueprint('social', __name__)

from app.social import flickr
