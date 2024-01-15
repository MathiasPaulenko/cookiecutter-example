import datetime
import json

from sqlalchemy import text
from flask import render_template, request

from arc.web.app.executions.forms import FilterExecutionsForm
from arc.web.extensions import db
from arc.web.app.executions import bp as executions_bp
from arc.web.models.models import Execution


@executions_bp.route('/executions/')
def executions():
    """
        Executions view, return a paginated list of all the executions saved.
    :return:
    """
    _args = {}
    _executions = []
    filter_form = FilterExecutionsForm(**request.args)

    if len(request.args) > 0 and any(list(request.args.values())):
        order = request.args.get('order')
        status = request.args.get('status')
        id_from = request.args.get('id_from')
        id_to = request.args.get('id_to')
        environment = request.args.get('environment')

        exec_options = db.select(Execution)

        if status:
            if status == FilterExecutionsForm.status_choices[1]:
                exec_options = exec_options.where(Execution.features_failed == 0)
            elif status == FilterExecutionsForm.status_choices[2]:
                exec_options = exec_options.where(Execution.features_failed != 0)
        if id_from:
            exec_options = exec_options.where(Execution.id >= id_from)
        if id_to:
            exec_options = exec_options.where(Execution.id <= id_to)
        if environment:
            exec_options = exec_options.where(Execution.environment == environment)
        if order and order == FilterExecutionsForm.order_choices[1]:
            exec_options = exec_options.order_by(Execution.id.asc())
        else:
            exec_options = exec_options.order_by(Execution.id.desc())

        _executions = db.paginate(exec_options, max_per_page=20)
    else:
        _executions = db.paginate((db.select(Execution).order_by(Execution.id.desc())), max_per_page=20)

    for key, value in request.args.items():
        if key != 'page' and value != '':
            _args[key] = value

    return render_template(
        'executions/executions.html', page_title="All executions results",
        executions=_executions,
        active_page="results",
        form=filter_form,
        args=_args
    )


@executions_bp.route('/execution/<int:execution_id>/')
def get_execution(execution_id):
    """
        Given an id, try to return the execution associated either return the 404
    :param execution_id:
    :return:
    """
    execution = db.get_or_404(Execution, execution_id)
    return render_template(
        'executions/execution.html', page_title=f"Execution #{execution_id}",
        execution=execution,
        active_page="results"
    )


@executions_bp.route('/api/v1/executions/')
def get_executions_by_dates():
    """
        Given the url params from_date and to_date return the values needed to draw the Executions Statistics chart.
        If from_date is null, then use today - 5 days.
        If to_date is null, then use today.
    :return:
    """
    today = datetime.datetime.today()
    from_date = today if not request.args.get('from_date', False) else datetime.datetime.strptime(
        request.args.get('from_date'), '%Y-%m-%d')
    to_date = today if not request.args.get('to_date', False) else datetime.datetime.strptime(
        request.args.get('to_date'), '%Y-%m-%d')

    labels = []
    failed = []
    passed = []
    if from_date < to_date:
        _days = to_date - from_date
        start_date = from_date
    else:
        _days = from_date - to_date
        start_date = to_date
    for day in range(_days.days + 1):
        """
           We need the lists to looks like:
           [0,1,2,4,6]
           Where each value is the number of passed or failed values in that day.
           So given the from_date 18/07/2023 the first value will be associated to that date.
           The second value will be associated to the next day, 19/07/2023. 
        """
        final_date = (start_date + datetime.timedelta(days=day)).strftime("%Y-%m-%d")
        next_date = (start_date + datetime.timedelta(days=day + 1)).strftime("%Y-%m-%d")
        labels.append(final_date)
        _failed = db.session.execute(
            text(
                f"SELECT COUNT(id) as total_failed FROM {Execution.__tablename__}"
                f" WHERE {Execution.features_failed} > 0 AND {Execution.created_on} BETWEEN '{final_date}' and '{next_date}'"
            )
        ).first()[0]
        failed.append(_failed)
        _passed = db.session.execute(
            text(
                f"SELECT COUNT(id) as total_passed FROM {Execution.__tablename__}"
                f" WHERE {Execution.features_failed} == 0 AND {Execution.created_on} BETWEEN '{final_date}' and '{next_date}'"
            )
        ).first()[0]
        passed.append(_passed)

    return json.dumps({
        "failed": failed,
        "passed": passed,
        "labels": labels
    }, indent=4)
