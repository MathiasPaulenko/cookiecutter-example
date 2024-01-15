import os

from flask import render_template, redirect, url_for, flash, request

from arc.web.app.run.executions.routes import run_by_tag_process
from arc.web.app.run.run_tags import bp as run_tags_bp
from arc.web.app.run.form_feature_run import TagsExecutionForm
from arc.web.app.utils import get_all_tags, test_is_running


@run_tags_bp.route('/run/tags', methods=['GET', 'POST'])
def run_by_tag():
    """
    This route is used to show Run Groups Interface
    :return:
    """

    # Query all groups
    tags, failed = get_all_tags()
    form = TagsExecutionForm()
    if request.method == 'POST' and test_is_running() is False:
        if form.validate_on_submit():
            data = {
                "tags": form.data["tags"],
                "conf_file": form.data["conf_properties"].replace('-properties.cfg', ''),
                "params": ""
            }
            os.environ['pid'] = run_by_tag_process(**data)
            return redirect(url_for('.run_by_tag'))
        else:
            flash("Select at least 1 available tag.", 'error')
    return render_template(
        'run/run_by_tag.html', page_title="Run by tags",
        tags=tags, form=form, active_page="run",
        parsing_errors=failed,
        pid=os.environ.get('pid', '0'), portal_running=os.environ.get('RUNNING', 'False')
    )