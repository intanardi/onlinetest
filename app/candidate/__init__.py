from flask import Blueprint

candidate = Blueprint('candidate', __name__)

from . import views, errors