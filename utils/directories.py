# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: utils/directories.py

Description:
This module provides functions to initialize directories based on a given list
of directory paths and configuration settings. It includes logic to handle
conditional creation based on configuration options such as logging and database
settings.
"""

from typing import List, Dict
from pathlib import Path
from utils.logger import LoggerFactory


def initialize_directories(directories: List[str], config: Dict) -> None:
    """
    Initializes directories based on the provided list of directory paths.

    Args:
        directories (List[str]): A list of directory paths to be initialized.
        config (Dict): Configuration dictionary.

    Returns:
        None
    """
    logger = LoggerFactory.get_logger(config)
    logger.info("Initializing directories.")
    logger.debug(f"Directories to create: {directories}")

    for directory in directories:
        if not directory:
            continue  # Skip empty or None directory entries

        if 'logs' in directory and not config.get('logging', {}).get('log_to_file',
                                                                     True):
            logger.debug(
                "Logging to file is disabled in config. Skipping creation of directory.")
            continue

        if 'db' in directory and not config.get('database', {}).get('db_enabled', True):
            logger.debug(
                "Database is disabled in config. Skipping creation of directory.")
            continue

        directory_path = Path(directory)
        logger.debug(f"Checking existence of directory: {directory_path}")
        try:
            if not directory_path.exists():
                logger.debug(f"Creating directory: {directory_path}")
                directory_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {directory_path}")
            else:
                logger.debug(f"Directory already exists: {directory_path}")
        except Exception as e:
            logger.error(f"Error while initializing directory '{directory}': {e}")
            raise
