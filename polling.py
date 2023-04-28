import requests
import requests.auth
from credential import CLIENT_ID, CLIENT_SECRET


url = 'https://www.reddit.com/r/Thailand/search/?q='

# authenticate reddit app
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

# print(response.reason)
# print(response.json())
# print(response.json()['access_token'])


def get_query(keyword):
    access_token = response.json()['access_token']

    headers2 = {"Authorization": f"bearer {access_token}",
                "User-Agent": "polling/0.1"}

    params = {"q": keyword, "t": "year", "limit": 100}

    response2 = requests.get(
        "https://oauth.reddit.com/r/Thailand/search.json", headers=headers2, params=params)

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


# def get_query(name,timeframe):
#     res = requests.get(f"{url}{name}&t={timeframe}")

#     data = res


# get_query("prayuth","year")
