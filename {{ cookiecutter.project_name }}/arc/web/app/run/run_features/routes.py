import os

from flask import render_template, request, redirect, url_for, flash


from arc.web.app.run.executions.routes import run_feature_process,run_multiple_features_process
from arc.web.app.run.run_features import bp
from arc.web.app.run.form_feature_run import FeatureForm
from arc.web.app.utils import get_feature_files, test_is_running


@bp.route('/run/features', methods=['GET', 'POST'])
def run_features():
    """
        Prepares information for run features interface
    :return:
    """
    form = FeatureForm()
    files, failed = get_feature_files()
    data = {
        "files": files
    }

    if request.method == 'POST' and form.validate_on_submit() and test_is_running() is False:
        data = {
            "name": form.data["name_to_execute"],
            "conf_file": form.data["conf_properties"].replace('-properties.cfg', '')
        }
        os.environ['pid'] = run_feature_process(**data)
        return redirect(url_for('.run_features'))
    return render_template(
        'run/run_features.html', page_title="Run Features",
        data=data, form=form, active_page="run",
        pid=os.environ.get('pid', '0'),
        parsing_errors=failed,
        portal_running=os.environ.get('RUNNING', 'False')
    )


@bp.route('/run/multiple_features', methods=['GET', 'POST'])
def run_multiple_features():
    """
        Prepares information for run features interface
    :return:
    """
    form = FeatureForm()
    files, failed = get_feature_files()
    data = {
        "files": files
    }
    feature_names = request.form.getlist("Feature")
    if feature_names:
        if request.method == 'POST' and form.validate_on_submit() and test_is_running() is False:
            data = {
                "names": feature_names,
                "conf_file": form.data["conf_properties"].replace('-properties.cfg', '')
            }
            os.environ['pid'] = run_multiple_features_process(**data)
            return redirect(url_for('.run_features'))
    else:
        flash("You must select at least 1 feature in order to be executed.", 'error')
    return render_template(
        'run/run_features.html', page_title="Run Features",
        data=data, form=form, active_page="run",
        pid=os.environ.get('pid', '0'),
        parsing_errors=failed,
        portal_running=os.environ.get('RUNNING', 'False')
    )
