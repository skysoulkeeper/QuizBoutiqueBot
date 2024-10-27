# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: modules/categories.py

Description:
This module provides the CategoryHandler class, which manages category
directories within a specified questions directory. It includes functionality
to retrieve a list of subdirectories representing categories.
"""

from pathlib import Path
from typing import List


class CategoryHandler:
    """
    Class to handle categories by checking for subdirectories in a specified directory.
    """

    def __init__(self, questions_directory: Path, logger):
        """
        Initialize the CategoryHandler with the questions directory and logger.

        Args:
            questions_directory (Path): The path to the questions directory.
            logger: The logger instance for logging information and errors.
        """
        self.questions_directory = questions_directory
        self.logger = logger

    def get_categories(self) -> List[str]:
        """
        Get a list of category directories within the questions directory.

        Returns:
            List[str]: A list of category directory names.
        """
        if not self.questions_directory.exists():
            self.logger.error(
                f"Questions directory {self.questions_directory} does not exist.")
            return []

        self.logger.info(
            f"Checking for subdirectories in questions directory: {self.questions_directory}")
        return [d.name for d in self.questions_directory.iterdir() if d.is_dir()]


# Example usage
if __name__ == "__main__":
    from utils.initializer import Loader

    loader = Loader()
    config, logger = loader.initialize()

    questions_dir = Path(config['directories_to_create'][2])
    handler = CategoryHandler(questions_directory=questions_dir, logger=logger)
    categories = handler.get_categories()
    print(categories)
