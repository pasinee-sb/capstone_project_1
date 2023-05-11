from polling import generate_sentiment, plot_graph
from typing import List
from flask import Flask, request, jsonify, render_template, redirect, session, g, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import User, AnalysisCard, db, connect_db, Keyword, SentimentScore, Auth
from forms import KeywordForm, UserForm, LoginForm, AnalyzeForm, UserEditForm
from sqlalchemy.exc import IntegrityError
import os


CURR_USER_KEY = "curr_user"


app = Flask(__name__)
# app.app_context().push()
# uri = os.environ.get('DATABASE_URL', 'postgresql:///reddi-senti')
# app.config['SQLALCHEMY_DATABASE_URI'] = uri
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ECHO"] = True
# app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'mycapstone1')
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config.update(SESSION_COOKIE_SAMESITE="None",
#                   SESSION_COOKIE_SECURE=True)
# app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)

with app.app_context():

    uri = os.environ.get('DATABASE_URL', 'postgresql:///reddi-senti')

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'mycapstone1')
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config.update(SESSION_COOKIE_SAMESITE="None",
                      SESSION_COOKIE_SECURE=True)
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)


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

#    @app.before_request"""done for every request, such as
# checking if the user is logged in, or modifying the request object."""


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:

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
    - index.html: not logged in
    -redirect to user's page that shows Analyze machine : logged in"""
    if g.user:
        # show saved analysis cards

        return redirect(f"/users/{g.user.id}")

    return render_template('index.html')


@ app.route('/about')
def about():
    """render about page"""
    return render_template('about.html')


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

        user = User.register(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        do_login(user)
        flash('Your account has been created!', 'success')
        return redirect("/")

    else:
        return render_template('register.html', form=form)


@ app.route('/users/<int:user_id>/profile', methods=['GET', 'POST'])
def user_profile(user_id):
    """users may edit or delete own account"""
    if g.user.id == user_id:
        form = UserEditForm(obj=g.user)

        if form.validate_on_submit():
            user = User.authenticate(g.user.username, form.password.data)

            if user:
                g.user.username = form.username.data
                g.user.email = form.email.data
                db.session.commit()
                flash("User edited", "success")
                return redirect('/')

            else:
                flash("Edit unauthorized", "danger")
                return redirect('/')

        return render_template('edit_user.html', form=form)

    flash("Access not allowed", "danger")
    return redirect('/')


@app.route('/users/<int:user_id>')
def machine(user_id):
    """render Analyze machine for user if logged in else, return to root page"""
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


@ app.route('/demo')
def demo():
    """render demo """
    add_keyword_form = KeywordForm()
    form = AnalyzeForm()

    return render_template('machine.html',  add_keyword_form=add_keyword_form, form=form)


@app.route('/session')
def get_session():
    keywords = session.get('keywords', [])
    return jsonify({'keywords': keywords})


@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    """Add keyword to the keyword list"""
    keyword = request.json["word"]
    keywords = session.get('keywords', [])
    keywords.append(keyword)
    session['keywords'] = keywords

    return jsonify({'keywords': keywords})


@app.route('/remove_keyword/<keyword>', methods=['POST'])
def remove_keyword(keyword):
    """Remove keyword from keyword list"""
    try:
        keywords = session.get('keywords', [])
        keywords.remove(keyword)
        session['keywords'] = keywords

    except ValueError:
        pass

    if g.user:
        return redirect('/')
    return redirect('/demo')


@app.route('/analyze')
def analyze():
    """Analyze keyword by calculating sentiment scores"""
    # Get a list of keywords from checkbox values
    selected_keywords = request.args.getlist('keywords[]')
    err = "Unable to calculate score."
    results = []

    for word in selected_keywords:
        score = generate_sentiment(word)
        # If keyword retrieved from API can be used calculate mean sentiment scores
        # then it can be appended to the results list or else append error message
        if score:
            results.append(score)
        else:
            results.append(err)

    # Check if user is not logged in and if no keyword is checked on the checkbox then redirect back to the demo page
    if not g.user and len(selected_keywords) == 0:
        flash("Please check the keyword(s) to analyze", "danger")
        return redirect("/demo")

    # Check if not a logged in user, show results and show graph plotted according to calculation, if any errors then show errors
    elif not g.user:

        if err in results:
            flash(
                f"{err} Please ensure the keyword is spelled correctly or try a different keyword.", "danger")
            flash("Sign up or Log in to save result", "warning")
            return render_template('results.html', results=results, selected_keywords=selected_keywords, zip=zip)

        else:
            image_string = plot_graph(selected_keywords, results)

            flash("Sign up or Log in to save result", "warning")
            return render_template('results.html', results=results, selected_keywords=selected_keywords, zip=zip, image_string=image_string)

    # If it's a logged in user but no keywords were checked for analysis then redirect to the user's page
    elif g.user and len(selected_keywords) == 0:

        flash("Please check the keyword(s) to analyze", "danger")
        return redirect(f"/users/{g.user.id}")
    # If a logged in user, show results and show graph plotted according to calculation, if any errors then show errors
    elif g.user:
        if err in results:
            flash(
                f"{err} Please ensure the keyword is spelled correctly or try a different keyword.", "danger")
            return render_template('results.html', results=results, selected_keywords=selected_keywords, zip=zip)
        else:

            image_string = plot_graph(selected_keywords, results)

            return render_template('results.html', results=results, selected_keywords=selected_keywords, zip=zip, image_string=image_string)


@app.route('/users/<int:user_id>/cards', methods=['POST'])
def save_results(user_id):
    """save analysis results to user's dashboard"""
    err = "Result(s) not saved, please check spelling or change keyword "

    results = request.form.getlist('results[]')

    keywords = request.form.getlist('words[]')

    theme = request.form.get('theme')
    image_string = request.form.get('image_string')

    # loop through score in results, check if they are numeric or was an error passed on from /analyze
    # if not numeric value then flash warning for user to go back and change keyword
    for score in results:
        if not score.lstrip("-").replace(".", "").isnumeric():
            flash(err, "danger")
            return redirect("/")

    # if all scores are numeric then check if Analysis card's theme name already existed for that user
    existing_card = AnalysisCard.query.filter_by(
        analysis_theme=theme, user_id=user_id).first()

    if existing_card:
        flash("Analysis theme is taken, please change the theme", "danger")

        return render_template('results.html', results=results, selected_keywords=keywords, zip=zip, image_string=image_string)
    # if not already existing then add that analysis card to database for that user
    else:
        card = AnalysisCard(analysis_theme=theme,
                            user_id=user_id, image_string=image_string)

        db.session.add(card)
        db.session.commit()

    # loop through keywords and their matching scores and add them to the analysis card that was created on database

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
    """Show analysis card """

    # Check if the logged in user is the same user that owns the card
    if g.user.id == user_id:

        card = AnalysisCard.query.get(card_id)

        if card in g.user.analysis_card:
            # show card for authorized user
            return render_template('card.html', card=card, user_id=user_id, zip=zip)

        else:
            flash("This card does not belong to you", "danger")
    else:
        flash("Access not allowed", "danger")

    return redirect('/')


@ app.route('/users/<int:user_id>/cards/<int:card_id>/delete', methods=['POST'])
def delete_card(user_id, card_id):
    """Delete analysis card"""

    # Check if the person deleting the card is the person who logged in and owns the card
    if g.user.id == user_id:
        card = AnalysisCard.query.get(card_id)
        if card in g.user.analysis_card:
            g.user.analysis_card.remove(card)
            db.session.delete(card)
            db.session.commit()
            return redirect(f"/users/{user_id}/dashboard")

    flash("Access not allowed", "danger")

    return redirect("/")


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete user"""

    if g.user.id == user_id:
        user = User.authenticate(g.user.username, request.form.get('password'))
        if user:
            do_logout()
            db.session.delete(g.user)
            db.session.commit()
            flash("We are sorry to see you go", "danger")
            return redirect("/")
        else:
            flash("Re-type password to delete user", "danger")
            return redirect(f"/users/{user_id}/profile")
    else:
        flash("You are not authorized to delete this user.", "danger")
        return redirect("/")


@ app.route('/users/<int:user_id>/dashboard')
def show_user_dashboard(user_id):
    """Allows logged in users to view their own dashboard with their saved analysis cards"""

    if g.user.id == user_id:
        cards = AnalysisCard.query.filter_by(user_id=user_id).all()

        return render_template('dashboard.html', cards=cards)

    flash("Access not allowed", "danger")
    return redirect('/')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
