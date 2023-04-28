"""Forms for playlist app."""
from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm, model_form_factory
from models import Playlist, Song, PlaylistSong, db

BaseModelForm = model_form_factory(FlaskForm)
