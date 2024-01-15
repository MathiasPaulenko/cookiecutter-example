import logging
import os

from arc import get_installed_packages
from arc.core.test_method.exceptions import TalosNotThirdPartyAppInstalled, TalosConfigurationError
from arc.reports.html.utils import (get_duration, get_datetime_from_timestamp, get_date_or_time_from_timestamp,
                                    get_duration_from_timestamps)
from arc.settings.settings_manager import Settings
from arc.web.app.utils import check_settings_exists
from arc.web.config import Config, basedir


logger = logging.getLogger(__name__)


def create_app(config_class=Config, set_environ=True):
    """
        This function create the app, create the db if not exists, register the blueprints, extensions and then return
        the app generated.
    :param set_environ:
    :param config_class:
    :return:
    """
    check_packages()
    from flask import Flask
    # Models not used here but needed to create the tables in the database.
    from arc.web.models.models import Execution, ExecutionFeature, ExecutionScenario, ExecutionStep
    from arc.web.extensions import db
    from flask_migrate import Migrate
    from arc.web.app.home import bp as home_bp
    from arc.web.app.executions import bp as executions_bp
    from arc.web.app.run.run_features import bp as run_features_bp
    from arc.web.app.run.run_scenarios import bp as run_scenarios_bp
    from arc.web.app.run.run_custom_executions import bp as run_custom_executions_bp
    from arc.web.app.run.run_tags import bp as run_by_tags_bp
    from arc.web.app.run.executions import bp as view_executions_bp
    from arc.web.app.utilities import bp as utilities_bp
    from arc.web.app.help import bp as help_bp
    from arc.web.app.settings import bp as settings_bp
    from arc.web.app.profiles import bp as profiles_bp
    from arc.web.app.features import bp as features_bp
    logger.info("Initializing Flask app")

    if set_environ:
        os.environ['TALOS_PORTAL'] = 'True'
        os.environ['RUNNING'] = 'False'

    flask_app = Flask(
        'TalosBDDWeb',
        template_folder=f"{basedir}/templates",
        static_folder=f"{basedir}/static"
    )
    flask_app.config.from_object(config_class)
    logger.info("Registering filters for jinja2.")
    flask_app.jinja_env.filters['get_duration'] = get_duration
    flask_app.jinja_env.filters['format_datetime'] = get_datetime_from_timestamp
    flask_app.jinja_env.filters['format_date_or_time'] = get_date_or_time_from_timestamp
    flask_app.jinja_env.filters['get_duration_from_timestamps'] = get_duration_from_timestamps
    logger.info("Filters for jinja2 registered.")
    # Initialize Flask extensions here
    db.init_app(flask_app)
    flask_app.app_context().push()
    logger.info("Creating db and columns if not created")
    db.create_all()
    Migrate(flask_app, db)
    check_settings_exists()
    logger.info("DB Ready.")
    # Register blueprints here
    logger.info("Registering blueprints")
    flask_app.register_blueprint(home_bp)
    flask_app.register_blueprint(executions_bp)
    # Run Section
    flask_app.register_blueprint(run_features_bp)
    flask_app.register_blueprint(run_scenarios_bp)
    flask_app.register_blueprint(run_custom_executions_bp)
    flask_app.register_blueprint(run_by_tags_bp)
    flask_app.register_blueprint(view_executions_bp)
    flask_app.register_blueprint(help_bp)
    flask_app.register_blueprint(settings_bp)
    flask_app.register_blueprint(utilities_bp)
    flask_app.register_blueprint(profiles_bp)
    flask_app.register_blueprint(features_bp)
    logger.info("Blueprints registered")

    # Register error handlers
    logger.info("Registering 404 handler")
    flask_app.register_error_handler(404, page_not_found)
    logger.info("404 handler registered")
    if set_environ:
        msg = f" * Portal is available in http://localhost:{Settings.PYTALOS_WEB.get('port', default='5000')}"
        logger.info(msg)
        print(msg)
    return flask_app


def page_not_found(e):
    """
        If page not found, then return 404 html
    :param e:
    :return:
    """
    from flask import render_template
    return render_template("404.html"), 404


def check_packages():
    """
        This function checks if the needed_packages are installed in the venv.
        If not then raise a TalosNotThirdPartyAppInstalled exception.
    :return:
    """
    logger.info("Checking needed packages")
    packages = get_installed_packages()
    needed_packages = ['flask', 'flask-migrate', 'flask-sqlalchemy', 'sqlalchemy', 'flask-wtf', 'psutil']
    if not all(name in packages for name in needed_packages):
        logger.debug("Missing needed packages")
        raise TalosNotThirdPartyAppInstalled(
            "There are some packages that need to be"
            " installed in order to use the Portal."
            f"Make sure you have installed the following packages {needed_packages}"
        )


def main():
    """
    This main function start the creation of the app.
    :return:
    """
    flask_app = create_app()
    logger.info("Flask APP created")
    flask_app.run(
        debug=Settings.PYTALOS_WEB.get('debug', default=False),
        port=Settings.PYTALOS_WEB.get('port', default=5000)
    )


if __name__ == "__main__":
    main()
