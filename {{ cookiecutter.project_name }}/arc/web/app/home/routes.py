import logging

import flask
from flask import render_template, session
from arc.web.app.home import bp as home
from arc.web.app.utils import get_total_features_and_scenarios
from arc.web.extensions import db
from arc.web.models.models import Execution

logger = logging.getLogger(__name__)


@home.route('/')
def dashboard():
    """
        Dashboard view, return the last execution if exist and the total of executions, features, scenarios and steps.
    :return:
    """
    logger.info("Getting last execution")
    last_execution = db.session.execute(db.select(Execution).order_by(Execution.id.desc())).first()
    if last_execution:
        last_execution = last_execution[0]
    else:
        last_execution = None
    total_executions = Execution.query.count()
    logger.info(f"Total executions {total_executions}")
    total_features, total_scenarios, total_steps, failed = get_total_features_and_scenarios()
    return render_template(
        'home/home.html', page_title="",
        total_executions=total_executions,
        total_features=total_features,
        total_scenarios=total_scenarios,
        total_steps=total_steps,
        execution=last_execution,
        parsing_errors=failed,
        active_page="dashboard"
    )


@home.route('/set_dark_mode/')
def set_dark_mode():
    """
    Set the mode to dark
    TODO: Search a new way to set the dark mode. Maybe store in database.
    :return:
    """
    current_theme = session.get("dark_mode")
    if not current_theme:
        logger.info("Setting dark_mode to True")
        session["dark_mode"] = True
    elif current_theme is True:
        logger.info("Setting dark_mode to False")
        session["dark_mode"] = False

    return flask.Response(status=200)


