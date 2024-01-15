from flask import Blueprint

bp = Blueprint('help', __name__)

from arc.web.app.help import routes
