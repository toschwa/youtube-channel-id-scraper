CHANNEL_ID = "ABCDEFG"  # Replace with your channel ID
API_KEY = "ABCDEFG"  # Replace with your API key

#==============================================================================================================================
import urllib.request
import json
import os
API_URL = f"https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&channelId={CHANNEL_ID}&key={API_KEY}&maxResults=50"
ids = []
next_page_token = ""
total_results = None

while True:
    url = API_URL
    if next_page_token:
        url += f"&pageToken={next_page_token}"
    response = urllib.request.urlopen(url).read()
    data = json.loads(response.decode("utf-8"))

    ids.extend([
        item['snippet']['resourceId']['channelId']
        for item in data.get('items', [])
        if 'snippet' in item and 'resourceId' in item['snippet'] and 'channelId' in item['snippet']['resourceId']
    ])

    if total_results is None:
        total_results = data.get('pageInfo', {}).get('totalResults', 0)
        print(f"Total Channel IDs expected: {total_results}")

    next_page_token = data.get('nextPageToken')
    if not next_page_token:
        print(f"Total Channel IDs fetched: {len(ids)}")
        break

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "channels.yml"), "w") as f:
    for id in ids:
        f.write(f"- {id}\n")
    print("Done! Channel IDs saved to channels.yml")