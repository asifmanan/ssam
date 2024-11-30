import json

def load_config(file_path: str) -> dict:
    """
        Load the configuration from a JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)