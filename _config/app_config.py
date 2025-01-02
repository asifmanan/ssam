import json

class AppConfig:
    def __init__(self, config_file_path: str=None):
        """
        Initialize the AppConfig with the configuration file path.
        """
        if config_file_path==None:
            config_file_path = "_config/config.json"

        self.config = self.load_config(config_file_path)

    def load_config(self, file_path: str) -> dict:
        """
        Load and validate the configuration from a JSON file.

        :param file_path: Path to the configuration file.
        :return: Parsed configuration dictionary.
        """
        config=None
        try:
            with open(file_path, "r") as file:
                config = json.load(file)
        except Exception as e:
            print(f"Error loading configuration: {e}")

        # Validation checks
        if "network_config" not in config or not isinstance(config["network_config"], dict):
            raise ValueError("Invalid configuration: 'network_config' is missing or not a dictionary.")
        if "peers" not in config["network_config"] or not isinstance(config["network_config"]["peers"], list):
            raise ValueError("Invalid configuration: 'peers' is missing or not a list.")
        if "mining_config" not in config or not isinstance(config["mining_config"], dict):
            raise ValueError("Invalid configuration: 'mining_config' is missing or not a dictionary.")

        return config

    def get_network_config(self) -> dict:
        """
        Get the network configuration from the loaded configuration.
        """
        return self.config["network_config"]
    
    def get_mining_config(self) -> dict:
        """
        Get the mining configuration from the loaded configuration.
        """
        return self.config["mining_config"]
    
    def get_shard_config(self) -> dict:
        """
        Get the shard configuration from the loaded configuration.
        """
        return self.config["shard_config"]