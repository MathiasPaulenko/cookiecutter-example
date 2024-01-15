from flask import render_template, redirect, url_for

from arc.settings.settings_manager import Settings
from arc.web.app.profiles import bp
from arc.web.app.features.forms import EditFileForm, SaveFileForm
from arc.web.app.utils import get_all_files


@bp.route('/profile_files')
def view_profile_files():
    """
        Edit data for features
    :return:
    """
    path = f"{Settings.PROFILES_PATH.get(force=True)}"
    files = get_all_files(path)
    form = EditFileForm()
    data = {
        "files": files,
        "file_root": "Profiles"
    }
    return render_template(
        'profiles/view_profiles.html',
        page_title="Manage Data",
        data=data,
        edit_form=form,
        active_page="files"
    )


@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """
        Prepares information to edit the file passed in the form
    :return:
    """
    form = EditFileForm()
    form_save = SaveFileForm()
    if form.validate_on_submit():
        path_file = form.data["path_to_edit"]
        path_file = path_file.replace("\\", "/")
        file = path_file.split("/")
        file = file.pop()
        try:
            with open(path_file, 'r', encoding="utf-8") as fr:
                lines_file = fr.readlines()
        except Exception:
            lines_file = []

        data = {
            "file_lines": lines_file,
            "file_path": path_file,
            "type_file": file.split(".")[1]
        }
        return render_template(
            'profiles/edit_profile.html',
            page_title="Edit Files",
            data=data,
            form=form_save,
            active_page="files"
        )
    else:
        return redirect(url_for('.view_profile_files'))

