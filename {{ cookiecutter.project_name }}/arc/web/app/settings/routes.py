import copy
import json
import os

import flask
from flask import render_template, request, flash

from arc.core.config_manager import CustomConfigParser
from arc.core.test_method.exceptions import TalosConfigurationError
from arc.settings.settings_manager import Settings
from arc.web.app.settings.forms import SettingsForm, ConfigurationForm
from arc.web.app.utils import get_cfg_files
from arc.web.extensions import db
from arc.web.app.settings import bp as settings_bp
from arc.web.models.models import TalosSettings, DataType, SettingsValue


@settings_bp.route('/settings/')
def settings():
    """
        This view return the settings configuration list that allows to view and remove data.
        Includes also a button to go to settings creation form.
    :return:
    """
    _settings = db.paginate((db.select(TalosSettings).order_by(TalosSettings.id.desc())), max_per_page=20)
    return render_template('settings/settings.html', page_title="Settings", active_page='settings', _settings=_settings)


@settings_bp.route('/settings/<int:settings_id>', methods=['GET', 'POST'])
def edit_settings(settings_id):
    """
       This view allow to edit the setting with the following ID along with the values associates.
    :return:
    """
    _settings = db.get_or_404(TalosSettings, settings_id)

    # Given the setting_values set the fields to make it more dynamic
    form = SettingsForm

    if request.method == 'POST':
        form = form()
        if form.validate_on_submit():
            # Save data
            _settings.name = form.data['name']
            _settings.active = form.data['active']
            _settings.save()

            setting_values = _settings.get_setting_values_key_value()

            # Save settings values data.
            _values = []
            for key, value in form.data.items():
                if key in ['name', 'csrf_token', 'active']:
                    continue
                if setting_value := setting_values.get(key):
                    if setting_value.value != value:
                        setting_value.value = value
                        _values.append(setting_value)
                else:
                    _values.append(SettingsValue(**{
                        "setting_id": _settings.id,
                        "name": key,
                        "value": value,
                        "data_type": DataType.get_data_type_by_input_type(
                            input_type=form._fields[key].type
                        )
                    }))
                db.session.add_all(_values)
                db.session.commit()
            flash(f"Settings '{_settings.name}' saved.", "success")
            return flask.redirect(flask.url_for('.settings'))
    elif request.method == 'GET':
        data = {
            'settings_id': _settings.id,
            'name': _settings.name,
            'active': _settings.active
        }
        # Set the settings initial values to the form.
        data.update(SettingsForm.get_settings_values(_settings.setting_values))
        form = form(**data)
    return render_template(
        template_name_or_list='settings/edit_settings.html', page_title="Edit Settings",
        active_page='settings', _settings=_settings,
        form=form
    )


@settings_bp.route('/settings/new_settings/', methods=['GET', 'POST'])
def new_settings():
    """
        This view allow to create a new setting configuration.
        Accept GET and POST methods.
    :return:
    """
    form = SettingsForm(**SettingsForm.get_default_values())
    if request.method == 'POST' and form.validate_on_submit():
        _settings = TalosSettings(**{
            "name": form.data['name'],
            "active": form.data['active']
        })
        _settings.save()

        # Save settings values data.
        _values = []
        for key, value in form.data.items():
            if key in ['name', 'csrf_token', 'active']:
                continue
            _settings_value = SettingsValue(**{
                "setting_id": _settings.id,
                "name": key,
                "value": value,
                "data_type": DataType.get_data_type_by_input_type(
                    input_type=form._fields[key].type
                )
            })
            _values.append(_settings_value)
        try:
            db.session.add_all(_values)
            db.session.commit()
            flash(f"Settings '{_settings.name}' created.", "success")
            return flask.redirect(flask.url_for('.settings'))
        except (Exception, ) as ex:
            db.session.delete(_settings)
            db.session.commit()
            flash("There was an error during the creation of the new settings configuration.", "error")
    return render_template(
        template_name_or_list='settings/new_settings.html', page_title="Create settings",
        active_page='settings', form=form
    )


@settings_bp.route('/settings/delete/<int:settings_id>/', methods=['POST'])
def delete_settings(settings_id):
    """
    This view allows to delete a settings configuration given a settings_id.
    If the settings configuration is the last one in the database then doesn't delete it and add a message.
    :param settings_id:
    :return:
    """
    if TalosSettings.query.count() == 1:
        flash("Can't remove last settings configuration.", "error")
    else:
        _settings = db.get_or_404(TalosSettings, settings_id)
        settings_name = _settings.name
        db.session.delete(_settings)
        db.session.commit()
        flash(f"Settings '{settings_name}' removed.", "success")
    return flask.redirect(flask.url_for('.settings'))


@settings_bp.route('/configurations/')
def configuration_files():
    """
        This view return a list of all the .cfg files in the conf folder.
    :return:
    """
    prop_filenames = get_cfg_files()

    return render_template(
        template_name_or_list='settings/configuration_list.html', page_title="Configuration Files",
        active_page='settings', prop_files=prop_filenames
    )


@settings_bp.route('/configurations/<string:configuration_file>/', methods=['GET', 'POST'])
def edit_configuration_file_by_name(configuration_file):
    """
        This view allow to edit a cfg file and save the data in the file.
    :param configuration_file:
    :return:
    """
    cfg_file_path = os.path.join(Settings.CONF_PATH.get(force=True), configuration_file)

    # Create new class inhering from ConfigurationForm in order to avoid the modification of the original class.
    class CustomConfigurationForm(ConfigurationForm):
        pass

    form = CustomConfigurationForm
    try:
        # Get the cfg file and extract the data
        config = CustomConfigParser.get_config_from_file(cfg_file_path)
        current_data = config.get_section_values()
    except TalosConfigurationError:
        flash(f"The cfg file with name '{configuration_file}' doesn't exist."
              f"Please, provide a proper cfg file name", "error")
        return flask.redirect(flask.url_for('.configuration_files'))

    # Set form fields
    for section, values in current_data.items():
        for option, value in values.items():
            input_type, input_data = form.prepare_configuration_inputs(section, option, value)
            setattr(form, f"{section}_{option}", input_type(**input_data))

    if request.method == 'POST':
        # If post and form is valid, then update the values of the
        form = form()
        if form.validate_on_submit():

            # Do a copy of the form dict, remove no necessary keys and then try to update the options.
            custom_sections_inputs = json.loads(form.data['custom_sections_inputs'])
            remove_sections_inputs = json.loads(form.data['remove_sections_inputs'])
            _form_data = copy.copy(form.data)
            del _form_data['custom_sections_inputs']
            del _form_data['remove_sections_inputs']
            del _form_data['csrf_token']
            config.update_section_options_from_dict(current_data, _form_data)

            # Add new possible sections and options and try to remove selected sections or options.
            config.add_sections_and_options_form_dict(custom_sections_inputs)
            config.remove_sections_and_options_from_dict(remove_sections_inputs)

            with open(cfg_file_path, mode='w', encoding='utf8') as fp:
                config.write(fp=fp)
            flash(f"The cfg file '{configuration_file}' was updated successfully", 'success')
            return flask.redirect(flask.url_for('settings.configuration_files'))
    else:
        form = form()
    return render_template(
        template_name_or_list='settings/edit_configuration.html', page_title="Edit configuration",
        active_page='settings', configuration_file_name=configuration_file,
        section_values=current_data, form=form, sections=config.sections()
    )
