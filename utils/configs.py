# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: utils/configs.py

Description:
This module provides functionality to load and monitor configuration files
using YAML format. It includes classes for loading configurations and handling
file modifications in real-time.
"""

import sys
from typing import Dict, Callable, Optional
from pathlib import Path
import yaml
from watchdog.events import FileSystemEventHandler


class ConfigLoader:
    """
    Class to load configuration from YAML files.
    """

    def __init__(self, config_directory: Path):
        self.config_directory = Path(config_directory).resolve()
        self.config_path = self.config_directory / 'config.yml'
        self.dev_config_path = self.config_directory / 'config.dev.yml'

    def load_config(self) -> Dict[str, any]:
        """
        Load the configuration from a YAML file.

        Returns:
            Dict[str, any]: The loaded configuration.

        Raises:
            SystemExit: If the configuration file is not found or cannot be read.
        """
        actual_config_path = self.dev_config_path if self.dev_config_path.exists() else self.config_path
        try:
            with open(actual_config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            sys.stdout.write(
                f"Successfully loaded configuration from {actual_config_path}\n")
            return config
        except FileNotFoundError as e:
            sys.stderr.write(f"Configuration file not found: {e}\n")
            sys.exit(1)
        except yaml.YAMLError as e:
            sys.stderr.write(f"Error reading YAML file: {e}\n")
            sys.exit(1)


class ConfigFileHandler(FileSystemEventHandler):
    """
    Class to handle modifications to the configuration file.
    """

    def __init__(self, config_loader: ConfigLoader,
                 on_change_callback: Optional[Callable[[Dict[str, any]], None]] = None):
        self.config_loader = config_loader
        self.on_change_callback = on_change_callback

    def on_modified(self, event):
        """
        Callback method for file modification events.

        Args:
            event: The file system event.
        """
        if event.src_path == str(
                self.config_loader.config_path) or event.src_path == str(
                self.config_loader.dev_config_path):
            config = self.config_loader.load_config()
            if self.on_change_callback:
                self.on_change_callback(config)


# Example usage
if __name__ == "__main__":
    config_loader = ConfigLoader(Path("./configs"))
    config = config_loader.load_config()
    print(config)
