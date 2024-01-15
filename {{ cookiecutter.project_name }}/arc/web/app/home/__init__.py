import logging

from flask import Blueprint
logger = logging.getLogger(__name__)

logger.info("Creating blue print home")
bp = Blueprint('home', __name__)
logger.info("Blue print home created")

from arc.web.app.home import routes
