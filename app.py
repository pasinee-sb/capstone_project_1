
from polling import get_query
from textblob import TextBlob
import preprocessor as p
from statistics import mean
from typing import List
from flask import Flask, redirect, render_template, flash, make_response
from flask_debugtoolbar import DebugToolbarExtension
import csv


app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///twitter-poll'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# connect_db(app)


app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


def get_sentiment(all_posts: List[str]) -> List[float]:
    sentiment_scores = []
    for post in all_posts:
        blob = TextBlob(post)
        sentiment_scores.append(blob.sentiment.polarity)
        # sentiment_scores.append(blob)
        # print(sentiment_scores)
    return sentiment_scores


# # def generate_average_sentiment_score(keyword: str) -> int:
def get_mean_score(scores):

    average_score = mean(scores)
    return average_score


def generate_sentiment(name):
    all_posts = get_query(name)
    sentiment_scores = get_sentiment(all_posts)
    mean_score = get_mean_score(sentiment_scores)
    return (mean_score)


@app.route('/')
def show_home():
    score1 = generate_sentiment("pitha")
    score2 = generate_sentiment("prayuth")

    # second = generate_average_sentiment_score("prayuth")

    return render_template('index.html', score1=score1, score2=score2)
