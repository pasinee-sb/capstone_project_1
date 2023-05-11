import requests
import requests.auth
from credential import CLIENT_ID, CLIENT_SECRET
from typing import List
from statistics import mean, StatisticsError
from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt
import io
import base64


def authenticate_reddit():
    """authenticate reddit app"""
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {'grant_type': 'client_credentials',
                 'user': CLIENT_ID, 'password': CLIENT_SECRET}

    headers1 = {
        'User-Agent': 'A custom polling device'
    }

    # getting token access id
    TOKEN_ACCESS_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'

    response = requests.post(TOKEN_ACCESS_ENDPOINT,
                             data=post_data, headers=headers1, auth=client_auth)
    return response


def get_request_permission():
    """send get request headers to api"""

    response = authenticate_reddit()

    access_token = response.json()['access_token']

    headers2 = {"Authorization": f"bearer {access_token}",
                "User-Agent": "polling/0.1"}

    return headers2


def get_query(keyword: str) -> List[str]:
    """get reddit list of reddit posts associated to keyword"""

    headers2 = get_request_permission()

    params = {"q": keyword, "t": "year", "limit": 200}

    response2 = requests.get(
        "https://oauth.reddit.com/search.json", headers=headers2, params=params)

    data = response2.json()
    posts = data['data']['children']
    after_key = data['data']['after']
    before_key = data['data']['before']

    posts = []
    for item in data["data"]["children"]:
        post = {
            "title": item["data"]["title"],
            "selftext": item["data"]["selftext"]
        }
        posts.append(post['title'])
        posts.append(post['selftext'])

    return (posts)


def get_sentiment(all_posts: List[str]) -> List[float]:

    sentiment_scores = []
    for post in all_posts:
        blob = TextBlob(post)
        sentiment_scores.append(blob.sentiment.polarity)

    return sentiment_scores


# # def generate_average_sentiment_score(keyword: str) -> int:
def get_mean_score(scores):

    try:
        average_score = mean(scores)
        return round(average_score, 2)
    except StatisticsError:
        return None


def generate_sentiment(name):
    all_posts = get_query(name)
    sentiment_scores = get_sentiment(all_posts)
    mean_score = get_mean_score(sentiment_scores)
    return (mean_score)


def plot_graph(x, y):
    fig, ax = plt.subplots()
    ax.bar(x, y, width=0.3)
    plt.xticks(rotation=45)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_string = base64.b64encode(buffer.getvalue()).decode()
    return image_string
