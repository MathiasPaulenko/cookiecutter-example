import logging
import os
import random
import string

from arc.settings.settings_manager import Settings

basedir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)


class Config:
    """
        Base config class for the Flask app.
        Needed to create the Flask app.
    """
    logger.info("Set data in Config")
    SECRET_KEY = os.environ.get('SECRET_KEY', ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
    DATABASE_PATH = f"{Settings.BASE_PATH.get(force=True)}/{Settings.PYTALOS_WEB.get('database_name')}"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
