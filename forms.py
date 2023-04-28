"""Forms for reddit-poll app."""

from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm, model_form_factory
from models import User, SentimentAnalysis, AnalysisCard, AnalysisCardKeyword, Keyword, db

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm (BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class UserForm(ModelForm):
    """User Form"""
    class Meta:
        model = User


class KeywordForm(ModelForm):
    """Keyword form"""
    class Meta:
        model = Keyword
