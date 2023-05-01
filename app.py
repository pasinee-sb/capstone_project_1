from polling import generate_sentiment
from typing import List
from flask import Flask, request, jsonify, render_template, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import User, AnalysisCard, db, connect_db, Keyword, SentimentScore, Auth
from forms import KeywordForm, UserForm
import os

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///reddit-poll'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


# connect to database
connect_db(app)


app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

##############################################################################
# User signup/login/logout

#    @app.before_request""" is a decorator in Flask that registers a function to be called before each request
# is processed by the server. This can be used to perform tasks that
#  should be done for every request, such as setting up a database connection,
# checking if the user is logged in, or modifying the request object."""


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:

        # The g object in Flask is a global object that can be used to store data during the lifetime of a request.
        # It is often used to store objects that need to be accessed by multiple functions during the handling of a request.
        # The g object is specific to each request and is not shared between different requests.
        # It is created at the start of a request and destroyed at the end of the request.
        g.user = User.query.get(session[CURR_USER_KEY])

    else:

        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:

        del session[CURR_USER_KEY]


# @app.route('/', method=['GET', 'POST'])
# def home():
#     form = UserForm()
#     if form.validate_on_submit():
#         try:

#             user = User.register(username=form.username.data,
#                            password=form.password.data)
#         return redirect(f"/user/{user.id}")

#     return render_template('register.html', form=form)
