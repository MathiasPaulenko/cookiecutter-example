from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms.validators import DataRequired


class SaveFileForm(FlaskForm):
    file_content = HiddenField("content", validators=[DataRequired()])
    path = HiddenField("path", validators=[DataRequired()])


class EditFileForm(FlaskForm):
    path_to_edit = HiddenField("path", validators=[DataRequired()])
    page_to_back = HiddenField("page_back", validators=[DataRequired()])