from typing import List, Dict
import json
class Channel:
    def __init__(self, channel_id: str, title: str):
        self.channel_id = channel_id
        self.title = title

    def __repr__(self) -> str:
        return f"Channel(id={self.channel_id}, title={self.title})"

class Config:
    def __init__(self, api_key: str = "", channel_id: str = "", output_file: str = "channels.yml"):
        self.api_key = api_key
        self.channel_id = channel_id
        self.output_file = output_file
    def __repr__(self) -> str:
        return f"Config(api_key={self.api_key}, channel_id={self.channel_id}, output_file={self.output_file})"
    def write_to_disk(self, file_path: str):
        try:
            with open(file_path, 'w') as f:
                json.dump(self.__dict__, f)
        except IOError as e:
            raise IOError(f"Failed to write config to {file_path}.\n{e}")
    def read_from_disk(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.api_key = data.get('api_key', "")
                self.channel_id = data.get('channel_id', "")
                self.output_file = data.get('output_file', "channels.yml")
        except FileNotFoundError:
            print(f"Config file {file_path} not found.")

def parse_channel_data(data: List[Dict]) -> List[Channel]:
    channels = []
    for item in data:
        channel_id = item['snippet']['resourceId']['channelId']
        title = item['snippet']['title']
        channels.append(Channel(channel_id, title))
    return channels