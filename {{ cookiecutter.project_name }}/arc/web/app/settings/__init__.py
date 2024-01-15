import logging

from flask import Blueprint
logger = logging.getLogger(__name__)

logger.info("Creating blue print run_features")
bp = Blueprint('settings', __name__)
logger.info("Blue print run_features created")

from arc.web.app.settings import routes
