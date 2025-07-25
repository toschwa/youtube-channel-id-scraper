from typing import List, Dict

class Channel:
    def __init__(self, channel_id: str, title: str):
        self.channel_id = channel_id
        self.title = title

    def __repr__(self) -> str:
        return f"Channel(id={self.channel_id}, title={self.title})"

class Config:
    def __init__(self, api_key: str, channel_id: str):
        self.api_key = api_key
        self.channel_id = channel_id

    def __repr__(self) -> str:
        return f"Config(api_key={self.api_key}, channel_id={self.channel_id})"

def parse_channel_data(data: List[Dict]) -> List[Channel]:
    channels = []
    for item in data:
        channel_id = item['snippet']['resourceId']['channelId']
        title = item['snippet']['title']
        channels.append(Channel(channel_id, title))
    return channels