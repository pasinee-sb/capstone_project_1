import requests
import requests.auth
from credential import CLIENT_ID, CLIENT_SECRET
from typing import List
from statistics import mean
from textblob import TextBlob


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

    params = {"q": keyword, "t": "year", "limit": 100}

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
            "permalink": item["data"]["permalink"]
        }
        posts.append(post['title'])

    return (posts)


def get_sentiment(all_posts: List[str]) -> List[float]:

    sentiment_scores = []
    for post in all_posts:
        blob = TextBlob(post)
        sentiment_scores.append(blob.sentiment.polarity)

    return sentiment_scores


# # def generate_average_sentiment_score(keyword: str) -> int:
def get_mean_score(scores):

    average_score = mean(scores)
    return round(average_score, 2)


def generate_sentiment(name):
    all_posts = get_query(name)
    sentiment_scores = get_sentiment(all_posts)
    mean_score = get_mean_score(sentiment_scores)
    return (mean_score)
