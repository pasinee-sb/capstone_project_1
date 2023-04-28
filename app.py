from polling import generate_sentiment
from typing import List
from flask import Flask, redirect, render_template, flash, make_response, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import User, AnalysisCard, db, connect_db, Keyword, AnalysisCardKeyword
from forms import KeywordForm
import os

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


@app.route('/')
def home():
    form = KeywordForm()
    return render_template('index.html', form=form)


@app.route('/add', methods=['GET', 'POST'])
def add_keyword():
    # score1 = generate_sentiment("pitha")
    # score2 = generate_sentiment("paetongtarn")

    # if there are existing keywords, render them
    keywords = Keyword.query.all()
    all_words = [keyword.serialize() for keyword in keywords]
    print("#########################################")
    print(keywords)

    form = KeywordForm()

    if form.validate_on_submit():
        word = request.json["word"]
        keyword = Keyword(word=word)
        db.session.add(keyword)
        db.session.commit()

        response_json = jsonify(word=keyword.serialize())
        return (response_json, 201)

    return jsonify(words=all_words)
