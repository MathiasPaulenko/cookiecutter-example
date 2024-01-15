from flask import Blueprint

bp = Blueprint('features', __name__)

from arc.web.app.features import routes
