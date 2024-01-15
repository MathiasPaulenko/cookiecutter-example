from flask import Blueprint

bp = Blueprint('run_tags', __name__)

from arc.web.app.run.run_tags import routes
