import logging

from flask import Blueprint

logger = logging.getLogger(__name__)

logger.info("Creating blue print utilities")
bp = Blueprint('utils', __name__)

logger.info("Blue print utilities created")

from arc.web.app.utilities import routes
