import urllib.request
import json
import os
from datetime import datetime, timezone
from main import CONFIG_FILE

def fetch_channel_ids():
    if CONFIG_FILE.channel_id == "":
        raise ValueError("Channel ID is not set in the configuration file.")
    if CONFIG_FILE.api_key == "":
        raise ValueError("API key is not set in the configuration file.") 
    
    API_URL = f"https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&channelId={CONFIG_FILE.channel_id}&key={CONFIG_FILE.api_key}&maxResults=50"
    channels = []
    next_page_token = ""
    while True:
        url = API_URL
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        response = urllib.request.urlopen(url).read()
        data = json.loads(response.decode("utf-8"))

        channels.extend([
            {
                "id": item['snippet']['resourceId']['channelId'],
                "title": item['snippet']['title'],
                "publishedAt": item['snippet'].get('publishedAt'),
                "thumbnail": item['snippet'].get('thumbnails', {}).get('default', {}).get('url')
            }
            for item in data.get('items', [])
            if 'snippet' in item and 'resourceId' in item['snippet'] and 'channelId' in item['snippet']['resourceId']
        ])

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return channels

def save_new_channels_to_file(channels, output_file):
    # Get last write time
    if os.path.exists(output_file):
        last_write = datetime.fromtimestamp(os.path.getmtime(output_file), timezone.utc)
    else:
        last_write = datetime.min

    def parse_published_at(published_at):
        try:
            return datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")

    new_channels = [
        ch for ch in channels
        if ch.get("publishedAt") and parse_published_at(ch["publishedAt"]) > last_write
    ]

    if not new_channels:
        print("No new channels to append.")
        return

    with open(output_file, "a", encoding="utf-8") as f:
        for ch in new_channels:
            f.write(f"- {ch['id']} #{ch['title']}\n")
    print(f"Appended {len(new_channels)} new channels to {output_file}")