from flask import Blueprint

bp = Blueprint('executions', __name__)

from arc.web.app.executions import routes