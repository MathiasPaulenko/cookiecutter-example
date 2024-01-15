from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, IntegerField, FloatField, SelectField, HiddenField
from wtforms.validators import InputRequired

from arc.web.app.utils import get_available_profiles
from arc.web.models.models import DataType


class FilterExecutionsForm(FlaskForm):
    """
    This class allows to create a form for a CFG file.
    """
    order_choices = ['', 'ascendent', 'descendent']
    status_choices = ['', 'passed', 'failed']
    env_choices = [''] + get_available_profiles()
    order = SelectField('Order: ', choices=order_choices)
    id_from = IntegerField('From:')
    id_to = IntegerField('To:')
    status = SelectField('Status: ', choices=status_choices)
    environment = SelectField('Environment: ', choices=env_choices)
