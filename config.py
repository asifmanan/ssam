import json

def load_config(file_path: str) -> dict:
    """
    Load and validate the configuration from a JSON file.

    :param file_path: Path to the configuration file.
    :return: Parsed configuration dictionary.
    """
    try:
        with open(file_path, "r") as file:
            config = json.load(file)

        # Validation checks
        if "listen_addr" not in config:
            raise ValueError("Missing 'listen_addr' in configuration.")
        if "peers" not in config or not isinstance(config["peers"], list):
            raise ValueError("Invalid or missing 'peers' list in configuration.")

        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        raise