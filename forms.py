"""Forms for reddit-poll app."""

from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm, model_form_factory
from wtforms.fields import PasswordField, StringField, SubmitField, FieldList, EmailField
from wtforms.validators import DataRequired, Email
from models import User, SentimentScore, Keyword, db

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm (BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class UserForm(ModelForm):
    """User Form"""
    class Meta:
        model = User
    email = EmailField(validators=[DataRequired(), Email()])

    password = PasswordField(validators=[DataRequired()])


class UserEditForm(ModelForm):
    """User Form"""

    class Meta:
        model = User
    email = EmailField(validators=[DataRequired(), Email()])

    password = PasswordField(validators=[DataRequired()])


class LoginForm(ModelForm):
    """Login Form"""
    username = StringField(validators=[DataRequired()])

    password = PasswordField(validators=[DataRequired()])


class KeywordForm(ModelForm):
    """Keyword form"""
    class Meta:
        model = Keyword


class AnalyzeForm(FlaskForm):
    keywords = FieldList(StringField('Keyword', validators=[
                         DataRequired()]), min_entries=1)
    submit = SubmitField('Analyze')


class EditKeywordForm(FlaskForm):
    keyword = StringField('Keyword', validators=[DataRequired()])
    submit = SubmitField('Save')


class RemoveKeywordForm(FlaskForm):
    submit = SubmitField('Remove')
