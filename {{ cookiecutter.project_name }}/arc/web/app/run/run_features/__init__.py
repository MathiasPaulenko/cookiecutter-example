from flask import Blueprint

bp = Blueprint('run_features', __name__)

from arc.web.app.run.run_features import routes
