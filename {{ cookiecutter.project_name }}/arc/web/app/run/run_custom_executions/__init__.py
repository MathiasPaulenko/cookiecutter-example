from flask import Blueprint

bp = Blueprint('run_custom_executions', __name__)

from arc.web.app.run.run_custom_executions import routes
