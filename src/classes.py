import json

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
