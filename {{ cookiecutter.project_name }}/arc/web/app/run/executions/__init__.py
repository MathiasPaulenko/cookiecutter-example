from flask import Blueprint

bp = Blueprint('view_executions', __name__)

from arc.web.app.run.executions import routes
