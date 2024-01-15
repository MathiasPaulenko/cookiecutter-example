import os

from flask import render_template, jsonify, request, Response, redirect, url_for, flash
from arc.web.app.run.executions import bp
from arc.web.app.runners import execute_feature, execute_by_tags, execute_features, execute_by_scenario_names
from arc.web.app.utils import get_message, update_messages, clean_messages, send_request_portal, kill, get_alert, \
    update_alert, clean_alerts, get_info, update_info
from multiprocessing import Process
from arc.web.app.run.form_feature_run import StopExecutionForm

messages = []


@bp.route('/get_messages')
def get_messages():
    """
    Return a json with the messages stored in the messages global variable.
    :return:
    """
    status = os.environ.get('RUNNING', 'False')
    return jsonify({'messages': get_message(), 'status': status})


@bp.route('/view-executions', methods=['GET', 'POST'])
def view_executions():
    """
    Show View Executions interface
    :return:
    """
    if request.method == 'POST':
        log = update_messages(request.data.decode('utf-8'))
    else:
        log = get_message()
    data = {}
    pid = os.environ.get('pid', '0')
    form = StopExecutionForm(pid=pid)

    return render_template(
        'run/executions.html',
        page_title="Log", data=data, active_page="run", messages=log, running=os.environ['RUNNING'],
        pid=pid, form=form
    )


@bp.route('/get_alerts')
def get_alerts():
    """
    Return a json with the alerts stored in the alerts global variable.
    :return:
    """
    status = os.environ.get('RUNNING', 'False')
    return jsonify({'messages': get_alert(), 'status': status})


@bp.route('/get_infos')
def get_infos():
    """
    Return a json with the alerts stored in the alerts global variable.
    :return:
    """
    # status = os.environ.get('RUNNING', 'False')
    return jsonify({'messages': get_info()})


@bp.route('/send-alerts', methods=['GET', 'POST'])
def send_alerts():
    """
    Show alerts
    :return:
    """
    if request.method == 'POST':
        update_alert(request.data.decode('utf-8'))
    dict_send = {'key': 'RUNNING', 'value': 'False'}
    send_request_portal('post', 'json', dict_send, '/api/change-env')


@bp.route('/send-info', methods=['GET', 'POST'])
def send_infos():
    """
    Show alerts
    :return:
    """
    if request.method == 'POST':
        update_info(request.data.decode('utf-8'))
        return Response(status=200)


@bp.route('/api/change-env', methods=['POST'])
def finish_executions():
    """
    Finish executions
    :return:
    """
    data = eval(request.data.decode('utf-8'))
    os.environ[data['key']] = str(data['value'])
    if data['key'] == 'RUNNING' and data['value'] == 'False':
        os.environ['pid'] = "0"
    return Response(status=200)


@bp.route('/stop_execution', methods=['GET', 'POST'])
def stop_execution():
    form = StopExecutionForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.data['pid'] == os.environ.get('pid', '0'):
            kill(form.data['pid'])
            os.environ['pid'] = "0"
            os.environ['RUNNING'] = 'False'
            flash("Execution stopped", "error")
            update_messages("\nUser has stopped the execution")
        else:
            flash("PID not found", "error")
    return redirect(url_for('.view_executions'))


def run_feature_process(name, conf_file):
    """
        Start a process of execution for features and return the PID of the execution
        takes 2 arguments "name" of the feature and configuration file parameter
        Example:
         run_feature_process("host","chrome")
    :param name:
    :param conf_file:
    :return:
    """
    clean_messages()
    process = Process(target=execute_feature, args=(name, conf_file))
    process.start()
    dict_send = {'key': 'RUNNING', 'value': 'True'}
    send_request_portal('post', 'json', dict_send, '/api/change-env')
    return str(process.pid)


def run_multiple_features_process(names, conf_file):
    """
        Start a process of execution for features and return the PID of the execution
        takes 2 arguments "names" of the features and configuration file parameter
        Example:
         run_multiple_features_process(["demo_host","demo_mail"],"chrome")
    :param names:
    :param conf_file:
    :return:
    """
    clean_messages()
    process = Process(target=execute_features, args=(names, conf_file))
    process.start()
    dict_send = {'key': 'RUNNING', 'value': 'True'}
    send_request_portal('post', 'json', dict_send, '/api/change-env')
    return str(process.pid)


def run_by_tag_process(tags, conf_file, params):
    """
        Start a process of execution for tags executions and return the PID of the execution
        takes 2 arguments "tags" to execute and configuration file parameter
        The tags must be separated by commas.
        Example:
         run_by_tag_process("san_web1, san_web2","chrome")
    :param tags:
    :param conf_file:
    :param params:
    :return:
    """
    clean_messages()
    process = Process(target=execute_by_tags, args=(tags, conf_file, params))
    process.start()
    dict_send = {'key': 'RUNNING', 'value': 'True'}
    send_request_portal('post', 'json', dict_send, '/api/change-env')
    return str(process.pid)


def run_by_scenario_names_process(names, conf_file, params):
    """
        Start a process of execution for scenario executions and return the PID of the execution
        takes 2 arguments "names" of the scenarios and configuration file parameter
        Example:
         run_by_scenario_names_process(["Closing Markets, Navigation"],"chrome")
    :param names:
    :param conf_file:
    :param params:
    :return:
    """
    clean_messages()
    process = Process(target=execute_by_scenario_names, args=(names, conf_file, params))
    process.start()
    dict_send = {'key': 'RUNNING', 'value': 'True'}
    send_request_portal('post', 'json', dict_send, '/api/change-env')
    return str(process.pid)
