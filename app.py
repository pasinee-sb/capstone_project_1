from polling import generate_sentiment
from typing import List
from flask import Flask, request, jsonify, render_template, redirect, session, g, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import User, AnalysisCard, db, connect_db, Keyword, SentimentScore, Auth
from forms import KeywordForm, UserForm, LoginForm, AnalyzeForm, EditKeywordForm, RemoveKeywordForm, UserEditForm
import os

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///reddi-senti'
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

        session.clear()


@app.route('/')
def home():
    """Show homepage
    - anon users: not logged in
    -logged in : show keyword input form"""
    if g.user:
        # show saved analysis cards

        return redirect(f"/users/{g.user.id}")

    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('register.html', form=form)


@app.route('/users/<int:user_id>')
def machine(user_id):
    if g.user.id == user_id:

        add_keyword_form = KeywordForm()
        form = AnalyzeForm()

        return render_template('machine.html', add_keyword_form=add_keyword_form, form=form)

    flash("Access not allowed", "danger")
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def log_in():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username=form.username.data, pwd=form.password.data)

        if user:

            do_login(user)
            flash(f"Hello, {user.username}! Welcome back!", "success")
            return redirect(f"/users/{user.id}")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def log_out():

    do_logout()

    flash("See you later!", "success")
    return redirect('/')


@app.route('/add_keyword')
def add_keyword():
    keyword = request.args.get('word')
    keywords = session.get('keywords', [])
    keywords.append(keyword)
    session['keywords'] = keywords
    print(keyword)

    if g.user:
        return redirect('/')
    return redirect('/demo')


@app.route('/analyze')
def analyze():
    selected_keywords = request.args.getlist('keywords[]')

    results = []
    for word in selected_keywords:
        score = generate_sentiment(word)
        results.append(score)
    if g.user:
        return render_template('results.html', results=results, selected_keywords=selected_keywords, zip=zip)
    else:
        flash("Sign up or Log in to save result", "warning")
        return render_template('results.html', results=results, selected_keywords=selected_keywords, zip=zip)


@app.route('/edit_keyword')
def edit_keyword():
    form = EditKeywordForm()
    return None


@app.route('/remove_keyword/<keyword>')
def remove_keyword(keyword):
    try:
        keywords = session.get('keywords', [])
        keywords.remove(keyword)
        session['keywords'] = keywords

    except ValueError:
        pass

    if g.user:
        return redirect('/')
    return redirect('/demo')


@app.route('/users/<int:user_id>/cards', methods=['POST'])
def save_results(user_id):
    results = request.form.getlist('results[]')
    keywords = request.form.getlist('words[]')
    theme = request.form.get('theme')

    card = AnalysisCard(analysis_theme=theme, user_id=user_id)
    db.session.add(card)
    db.session.commit()
    for word, res in zip(keywords, results):
        keyword = Keyword(word=word)
        db.session.add(keyword)
        db.session.commit()
        result = SentimentScore(
            keyword_id=keyword.keyword_id, score=float(res), analysis_card_id=card.id)
        db.session.add(result)
        db.session.commit()
    return redirect(f"/users/{user_id}/cards/{card.id}")


@app.route('/users/<int:user_id>/cards/<int:card_id>')
def show_card(user_id, card_id):
    if g.user.id == user_id:

        card = AnalysisCard.query.get(card_id)

        if card in g.user.analysis_card:

            return render_template('card.html', card=card, user_id=user_id, zip=zip)

        else:
            flash("This card does not belong to you", "danger")
    else:
        flash("Access not allowed", "danger")

    return redirect('/')


@app.route('/users/<int:user_id>/cards/<int:card_id>/delete', methods=['POST'])
def delete_card(user_id, card_id):

    if g.user.id == user_id:
        card = AnalysisCard.query.get(card_id)
        if card in g.user.analysis_card:
            g.user.analysis_card.remove(card)
            db.session.commit()
            return redirect(f"/users/{user_id}/dashboard")

    flash("Access not allowed", "danger")

    return redirect("/")


@app.route('/users/<int:user_id>/profile', methods=['GET', 'POST'])
def user_profile(user_id):
    if g.user.id == user_id:
        form = UserEditForm(obj=g.user)

        if form.validate_on_submit():
            g.user.username = form.username.data
            g.user.email = form.email.data
            db.session.commit()
            flash("User edited", "success")
            return redirect('/')

        return render_template('edit_user.html', form=form)

    flash("Access not allowed", "danger")
    return redirect('/')


@app.route('/users/<int:user_id>/dashboard')
def show_user_dashboard(user_id):
    if g.user.id == user_id:
        cards = AnalysisCard.query.filter_by(user_id=user_id).all()

        return render_template('dashboard.html', cards=cards)

    flash("Access not allowed", "danger")
    return redirect('/')


@app.route('/about')
def about():

    return render_template('about.html')


@app.route('/demo')
def demo():
    add_keyword_form = KeywordForm()
    form = AnalyzeForm()

    return render_template('machine.html',  add_keyword_form=add_keyword_form, form=form)
