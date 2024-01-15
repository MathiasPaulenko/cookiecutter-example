import os

from flask import render_template, redirect, flash, url_for, request

from arc.web.app.run.executions.routes import run_by_tag_process,run_by_scenario_names_process
from arc.web.app.run.run_scenarios import bp
from arc.web.app.run.form_feature_run import TagsExecutionForm, ScenariosExecutionForm
from arc.web.app.utils import get_feature_files, test_is_running


@bp.route('/run/scenarios', methods=['GET', 'POST'])
def run_scenarios():
    """
        Prepares features information to run-scenarios interface
    :return:
    """
    form = ScenariosExecutionForm()
    files, failed = get_feature_files()
    data = {
        "files": files
    }
    if request.method == 'POST' and test_is_running() is False:
        if form.validate_on_submit():
            data = {
                "tags": form.data["tags"],
                "conf_file": form.data["conf_properties"].replace('-properties.cfg', ''),
                "params": ""
            }
            os.environ['pid'] = run_by_tag_process(**data)
            return redirect(url_for('.run_scenarios'))
        else:
            flash("The selected scenario need at least 1 tag in order to be executed.", 'error')
    return render_template(
        'run/run_scenarios.html', page_title="Run Scenarios",
        data=data, form=form, active_page="run",
        parsing_errors=failed,
        pid=os.environ.get('pid', '0'), portal_running=os.environ.get('RUNNING', 'False')
    )


@bp.route('/run/multiple_scenarios', methods=['GET', 'POST'])
def run_multiple_scenarios():
    """
        Prepares features information to run-scenarios interface
    :return:
    """
    form = ScenariosExecutionForm()
    files, failed = get_feature_files()
    data = {
        "files": files
    }
    scenario_names = request.form.getlist("Scenario")
    if scenario_names:
        if request.method == 'POST' and form.validate_on_submit() and test_is_running() is False:
            data = {
                "names": scenario_names,
                "conf_file": form.data["conf_properties"].replace('-properties.cfg', ''),
                "params": ""
            }
            os.environ['pid'] = run_by_scenario_names_process(**data)
            return redirect(url_for('.run_scenarios'))
    else:
        flash("You must select at least 1 scenario in order to be executed.", 'error')
    return render_template(
        'run/run_scenarios.html', page_title="Run Scenarios",
        data=data, form=form, active_page="run",
        parsing_errors=failed,
        pid=os.environ.get('pid', '0'), portal_running=os.environ.get('RUNNING', 'False')
    )
