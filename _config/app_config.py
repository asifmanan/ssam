import json
import logging


class AppConfig:
    def __init__(self, config_file_path: str = None):
        """
        Initialize the AppConfig with the configuration file path.
        """
        if config_file_path is None:
            config_file_path = "_config/config.json"

        self.config = self.load_config(config_file_path)

    def load_config(self, file_path: str) -> dict:
        """
        Load and validate the configuration from a JSON file.

        :param file_path: Path to the configuration file.
        :return: Parsed configuration dictionary.
        """
        try:
            with open(file_path, "r") as file:
                config = json.load(file)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

        required_keys = ["network_config", "mining_config", "shard_config", "stake_info"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Invalid configuration: '{key}' is missing.")

        return config

    def get_network_config(self) -> dict:
        return self.config["network_config"]

    def get_mining_config(self) -> dict:
        return self.config["mining_config"]

    def get_shard_config(self) -> dict:
        return self.config["shard_config"]

    def get_stake_info(self) -> dict:
        return self.config["stake_info"]

    def get_peers_for_shard(self, shard: str) -> list:
        """
        Get the list of peers for a given shard.
        :param shard: The shard identifier (e.g., "shard10").
        :return: List of peers for the shard.
        """
        shard_config = self.get_shard_config()
        peers = shard_config.get(shard, [])
        if not peers:
            logging.error(f"No peers found for shard {shard}. Check the shard configuration.")
        return peers
    
    def get_number_of_miners(self, shard_name: str) -> int:
        """
        Get the number of miner nodes in the specified shard.

        :param shard_name: The name of the shard 
        :return: The number of miner nodes in the shard.
        """
        shard_config = self.config.get("shard_config", {})
        peers = shard_config.get(shard_name, [])
        # Count entries in the shard that are miner nodes
        miner_count = sum(1 for peer in peers if "miner" in peer)
        return miner_count

    def get_staker_for_shard(self, shard: str) -> str:
        """
        Get the staker address for a given shard.
        :param shard: The shard identifier (e.g., "shard10").
        :return: The staker's address (e.g., "staker10:5000").
        """
        peers = self.get_peers_for_shard(shard)
        for peer in peers:
            if "staker" in peer:
                return peer
        raise ValueError(f"No staker found for shard {shard}.")
    
    def get_other_stakers(self, node_name: str) -> list:
        """
        Get a list of all stakers except the one specified by node_name.

        :param node_name: The name of the current staker node.
        :return: A list of other stakers in the network.
        """
        all_peers = self.config.get("network_config", {}).get("peers", [])
        other_stakers = [
            peer for peer in all_peers if "staker" in peer and not peer.startswith(node_name)
        ]
        return other_stakers