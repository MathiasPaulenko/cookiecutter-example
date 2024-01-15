from flask import Blueprint

bp = Blueprint('run_scenarios', __name__)

from arc.web.app.run.run_scenarios import routes
