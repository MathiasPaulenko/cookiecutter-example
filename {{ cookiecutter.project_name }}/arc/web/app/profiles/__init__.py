from flask import Blueprint

bp = Blueprint('profiles', __name__)

from arc.web.app.profiles import routes
