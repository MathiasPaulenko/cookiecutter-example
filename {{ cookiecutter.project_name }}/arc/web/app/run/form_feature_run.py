from flask_wtf import FlaskForm
from wtforms import HiddenField, BooleanField, StringField, SelectField
from wtforms.validators import DataRequired, ValidationError, InputRequired
from wtforms.widgets import HiddenInput

from arc.web.app.utils import get_cfg_files, get_available_profiles


class FeatureForm(FlaskForm):
    name_to_execute = HiddenField("feature name", validators=[DataRequired()])
    conf_properties = SelectField('Properties file', choices=get_cfg_files())


class MultipleFeaturesForm(FlaskForm):
    names_to_execute = HiddenField("feature names", validators=[DataRequired()])
    conf_properties = SelectField('Properties file', choices=get_cfg_files())


class TagsExecutionForm(FlaskForm):
    tags = StringField('Tags', validators=[DataRequired()], widget=HiddenInput())
    conf_properties = SelectField('Properties file', choices=get_cfg_files())

class ScenariosExecutionForm(FlaskForm):
    conf_properties = SelectField('Properties file', choices=get_cfg_files())


class StatusUpdateForm(FlaskForm):
    action = HiddenField("action", validators=[DataRequired()])
    pid = HiddenField("feature name", validators=[DataRequired()])


class StopExecutionForm(FlaskForm):
    pid = HiddenField("pid", validators=[DataRequired()])


class CustomExecutionForm(FlaskForm):
    id = HiddenField('Group id')
    name = StringField('Execution name', render_kw={"placeholder": "Execution name"}, validators=[InputRequired()])
    conf_properties = SelectField('Properties file', choices=get_cfg_files())
    headless = BooleanField('Headless', default=False)
    tags = StringField('Tags', validators=[DataRequired()], widget=HiddenInput())
    environment = SelectField('Environment', choices=get_available_profiles())
    extra_arguments = StringField('Extra arguments', render_kw={"placeholder": "-D Driver_type=firefox -p http://proxy:8080"})
    save_execution = BooleanField('Save execution', default=False, render_kw={"class": "d-none"})

    def validate_name(self, field):
        """
            If form have id, then field name is mandatory.
        """
        if self.data['save_execution'] and field.data.strip() == "":
            raise ValidationError("Field 'Configuration name' is mandatory when saving a custom execution")
