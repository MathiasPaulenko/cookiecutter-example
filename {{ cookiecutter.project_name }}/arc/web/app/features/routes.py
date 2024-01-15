import os
import pathlib

from flask import render_template, redirect, url_for

from arc.settings.settings_manager import Settings
from arc.web.app.features import bp
from arc.web.app.features.forms import EditFileForm, SaveFileForm
from arc.web.app.utils import get_step_list, get_all_files


@bp.route('/features')
def view_features():
    """
        Show features folder
    :return:
    """
    files = get_all_files(f"{Settings.TEST_PATH.get(force=True)}/features")
    form = EditFileForm()
    data = {
        "files": files,
        "file_root": "Features"
    }
    return render_template(
        'features/view_features.html',
        page_title="View Features",
        data=data,
        edit_form=form,
        active_page="files"
    )


@bp.route('/edit_feature', methods=['GET', 'POST'])
def edit_features():
    """
        Prepares information to edit the feature passed in the form
    :return:
    """
    form = EditFileForm()
    form_save = SaveFileForm()
    if form.validate_on_submit():
        path_file = form.data["path_to_edit"]
        path_file = path_file.replace("\\", "/")
        try:
            with open(path_file, 'r', encoding="utf-8") as fr:
                lines_file = fr.readlines()
        except Exception:
            lines_file = []
        steps = get_step_list()
        data = {
            "file_lines": lines_file,
            "steps": steps,
            "file_path": path_file,
            "type_file": "gherkin"
        }
        return render_template(
            'features/edit_features.html',
            page_title="Edit Feature",
            data=data,
            form=form_save,
            active_page="files"
        )
    else:
        return redirect(url_for('.view_features'))


@bp.route('/save_file', methods=['POST'])
def save_file():
    """
      Method to save the feature file.
      Receives a form with the new information to replace in the file
    :return:
    """
    form = SaveFileForm()
    if form.validate_on_submit():
        code = form.data["file_content"]
        path_file = form.data["path"]
        code = code.split("\\n")
        # If the file to save is new, then create the folders and file if needed.
        if not pathlib.Path(path_file).is_file():
            pathlib.Path(path_file).mkdir(parents=True, exist_ok=True)
        try:
            with open(path_file, 'w', encoding="utf-8") as wr:
                for line in code:
                    wr.write(line + "\n")
            return 'File saved'
        except FileNotFoundError:
            msg = "Error saving the file. File or route not found."
            print(msg)
            return msg
