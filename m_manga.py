import requests

def grab_rss_data():
    response = requests.get('https://api.mangadex.org/chapter?limit=50&offset=0&order[readableAt]=desc')
    data = response.json()
    chapters = [c['id'] for c in data['data']]
    return chapters
