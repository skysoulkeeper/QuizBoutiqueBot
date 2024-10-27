# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: utils/initializer.py

Description:
This module provides the main application initializer. It handles loading
configuration, setting up logging, proxy settings, localization, and
necessary directories. It also includes functionality for watching
configuration file changes and reloading the configuration dynamically.
"""

from pathlib import Path
from typing import Tuple, Any, Dict, Optional
from utils.configs import ConfigLoader, ConfigFileHandler
from utils.logger import LoggerFactory
from utils.directories import initialize_directories
from utils.proxy import ProxyHandler
from utils.localization import Localization
from watchdog.observers import Observer
import os


class Loader:
    """
    Class to initialize the application by loading configuration, setting up logging, proxy, and directories.
    """

    def __init__(self):
        config_directory = Path(__file__).parent.parent / 'configs'
        self.config_loader = ConfigLoader(config_directory)
        self.config = self.config_loader.load_config()
        self.environment = self.config['base_settings']['env']
        self.logger = self.setup_logging()
        self.proxy_handler = self.setup_proxy()
        self.localization = Localization(self.config['telegram']['language'])
        self.telegram_token = self.config['telegram']['token']
        self.telegram_chat_id = self.config['telegram']['chat_id']
        self.parse_mode = self.config['telegram'].get('parse_mode', 'HTML')
        self.config_observer = None
        if self.config.get('base_settings', {}).get('auto_reload_config_enabled', False):
            self.start_config_watcher()

    def setup_logging(self) -> Any:
        """
        Set up logging based on the loaded configuration.

        Returns:
            Logger instance.
        """
        return LoggerFactory.get_logger(self.config['logging'])

    def load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the configuration file.

        Returns:
            Loaded configuration dictionary.
        """
        config = self.config_loader.load_config()
        self.logger.info(
            f"Successfully reloaded configuration from {self.config_loader.config_path}")
        return config

    def create_directories(self) -> None:
        """
        Create necessary directories based on the loaded configuration.
        """
        directories = self.config.get('directories_to_create', [])
        initialize_directories(directories, self.config)

    def setup_proxy(self) -> Optional[ProxyHandler]:
        """
        Set up the proxy handler based on the loaded configuration.

        Returns:
            ProxyHandler instance if proxy is enabled, otherwise None.
        """
        proxy_config = self.config.get('proxy_settings', {})
        if proxy_config.get('proxy_enabled', False):
            proxy_handler = ProxyHandler(
                proxy_host=proxy_config.get('proxy_host'),
                proxy_port=proxy_config.get('proxy_port'),
                proxy_protocol=proxy_config.get('proxy_protocol', 'http'),
                proxy_username=proxy_config.get('proxy_username'),
                proxy_password=proxy_config.get('proxy_password'),
                config=self.config
            )
            proxy_handler.set_proxy()
            if proxy_handler.test_proxy_access():
                self.logger.info("Proxy is accessible.")
                os.environ['HTTP_PROXY'] = proxy_handler.proxy.get('http')
                os.environ['HTTPS_PROXY'] = proxy_handler.proxy.get('https')
            else:
                self.logger.error("Proxy is not accessible.")
            return proxy_handler
        else:
            self.logger.info("Proxy is disabled in configuration.")
            return None

    def start_config_watcher(self) -> None:
        """
        Start the configuration file watcher if auto-reload is enabled in the configuration.
        """
        event_handler = ConfigFileHandler(self.config_loader, self.on_config_change)
        self.config_observer = Observer()
        self.config_observer.schedule(event_handler,
                                      str(self.config_loader.config_path.parent),
                                      recursive=False)
        self.config_observer.start()
        self.logger.info("Started configuration file watcher.")

    def stop_config_watcher(self) -> None:
        """
        Stop the configuration file watcher.
        """
        if self.config_observer:
            self.config_observer.stop()
            self.config_observer.join()
            self.logger.info("Stopped configuration file watcher.")

    def on_config_change(self, new_config: Dict[str, Any]) -> None:
        """
        Callback function for handling configuration file changes.

        Args:
            new_config (Dict[str, Any]): The new configuration dictionary.
        """
        self.logger.info("Configuration file changed, applying new settings.")
        self.config = self.load_config()
        self.setup_proxy()

    def initialize(self) -> Tuple[
        Dict[str, Any], Any, Optional[ProxyHandler], Localization, str, str,
        Optional[Path], str]:
        """
        Initialize the application by setting up directories, proxy, and other necessary components.

        Returns:
            A tuple containing the configuration, logger, proxy handler, localization, telegram token, telegram chat id, questions directory path, and parse mode.
        """
        self.logger.info(
            f"Starting app initialization for {self.environment} environment")
        self.create_directories()
        self.setup_proxy()
        self.logger.info(
            f"App initialization complete for {self.environment} environment")
        questions_directory = next(
            (Path(d) for d in self.config['directories_to_create'] if
             'questions' in d),
            None)
        return self.config, self.logger, self.proxy_handler, self.localization, self.telegram_token, self.telegram_chat_id, questions_directory, self.parse_mode

# Example usage
if __name__ == "__main__":
    loader = Loader()
    config, logger, proxy_handler, localization, telegram_token, telegram_chat_id, questions_directory, parse_mode = loader.initialize()
    logger.info("Initialization complete")
