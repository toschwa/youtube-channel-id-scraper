import urllib.request
import json
import os
from datetime import datetime
from main import CONFIG_FILE

def load_config(config_file=CONFIG_FILE):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    with open(config_file, "r") as f:
        config = json.load(f)
    if "channel_id" not in config or "api_key" not in config or "output_file" not in config:
        raise KeyError("Config file must contain 'channel_id', 'api_key', and 'output_file'")
    return config["channel_id"], config["api_key"], config["output_file"]

def fetch_channel_ids(channel_id=None, api_key=None):
    # If not provided, load from config
    if channel_id is None or api_key is None:
        channel_id, api_key, _ = load_config()

    API_URL = f"https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&channelId={channel_id}&key={api_key}&maxResults=50"
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
        last_write = datetime.utcfromtimestamp(os.path.getmtime(output_file))
    else:
        last_write = datetime.min

    new_channels = [
        ch for ch in channels
        if ch.get("publishedAt") and datetime.strptime(ch["publishedAt"], "%Y-%m-%dT%H:%M:%SZ") > last_write
    ]

    if not new_channels:
        print("No new channels to append.")
        return

    with open(output_file, "a") as f:
        for ch in new_channels:
            f.write(f"- {ch['id']}\n")
    print(f"Appended {len(new_channels)} new channels to {output_file}")