import os

from flask import render_template, redirect, request, flash, url_for, jsonify

from arc.web.app.run.executions.routes import run_by_tag_process
from arc.web.app.run.run_custom_executions import bp
from arc.web.app.run.form_feature_run import CustomExecutionForm
from arc.web.app.utils import get_all_tags, test_is_running
from arc.web.models.models import CustomExecution
from arc.web.extensions import db


@bp.route('/run/custom', methods=['GET', 'POST'])
def run_custom_execution():
    """
    This method is used to show Run Groups Interface
    :return:
    """
    execution_form = CustomExecutionForm()
    if request.method == "POST" and test_is_running() is False:
        if execution_form.validate_on_submit():
            group_data = {
                "name": execution_form.data['name'].strip(),
                "conf_properties": execution_form.data['conf_properties'],
                "headless": execution_form.data['headless'],
                "tags": execution_form.data['tags'],
                "environment": execution_form.data['environment'],
                "extra_arguments": execution_form.data['extra_arguments'],
            }
            if execution_form.data['save_execution']:
                if execution_form.data['id'] != '' and int(execution_form.data['id']) > 0:
                    custom_execution = db.get_or_404(CustomExecution, execution_form.data['id'])
                    custom_execution.name = group_data['name']
                    custom_execution.conf_properties = group_data['conf_properties']
                    custom_execution.headless = group_data['headless']
                    custom_execution.tags = group_data['tags']
                    custom_execution.environment = group_data['environment']
                    custom_execution.extra_arguments = group_data['extra_arguments']
                    custom_execution.save()
                    flash("Custom Execution updated successfully.", "success")
                else:
                    new_execution = CustomExecution(**group_data)
                    new_execution.save()
                    flash(f"New Custom Execution with name '{new_execution.name}' created.", "success")
            else:
                # prepare the data and params
                data = {
                    "tags": execution_form.data["tags"],
                    "conf_file": execution_form.data["conf_properties"].replace('-properties.cfg', ''),
                    "params": f" -env {execution_form.data['environment']} {execution_form.data['extra_arguments']}"
                }
                if execution_form.data['headless']:
                    data['params'] += " -D Driver_headless='True'"
                os.environ['pid'] = run_by_tag_process(**data)
            return redirect(url_for('.run_custom_execution'))
        else:
            flash("Invalid data submitted, check the data and try again.", "error")

    # Query all groups
    executions = CustomExecution.query.all()
    tags, failed = get_all_tags()
    return render_template(
        'run/run_custom_execution.html', page_title="Custom Run",
        tags=tags, executions=executions, form=execution_form,
        pid=os.environ.get('pid', '0'),
        parsing_errors=failed,
        active_page="run", portal_running=os.environ.get('RUNNING', 'False')
    )


@bp.route("/api/custom_execution/<int:custom_execution_id>/")
def get_custom_execution_data(custom_execution_id):
    """
    Given a custom_execution_id return the json data of the custom execution
    :param custom_execution_id:
    :return:
    """
    custom_execution = db.get_or_404(CustomExecution, custom_execution_id)
    data = {
        "id": custom_execution.id,
        "name": custom_execution.name,
        "conf_properties": custom_execution.conf_properties,
        "headless": custom_execution.headless,
        "tags": custom_execution.tags,
        "environment": custom_execution.environment,
        "extra_arguments": custom_execution.extra_arguments
    }
    return jsonify(data)


@bp.route('/custom_execution/delete/<int:custom_execution_id>/', methods=['POST'])
def delete_custom_execution(custom_execution_id):
    """
    This view allows to delete a custom execution by id.
    :param custom_execution_id:
    :return:
    """
    custom_execution = db.get_or_404(CustomExecution, custom_execution_id)
    custom_execution_name = custom_execution.name
    db.session.delete(custom_execution)
    db.session.commit()
    flash(f"Custom execution '{custom_execution_name}' removed.", "success")
    return redirect(url_for('.run_custom_execution'))
