# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: utils/localization.py

Description:
This module provides a localization handler that manages the loading and
retrieval of translated strings from YAML files. It allows for language-specific
translation of strings, with support for dynamic formatting.
"""

import yaml
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Localization:
    """
    A class to handle localization by loading and retrieving translated strings.
    """
    language: str
    translations: Dict[str, str] = None

    def __post_init__(self):
        """
        Initialize the translations dictionary after the instance is created.
        """
        self.translations = self.load_translations(self.language)

    @staticmethod
    def load_translations(language: str) -> Dict[str, str]:
        """
        Load translations from a YAML file for the specified language.

        Args:
            language (str): The language code for which to load translations.

        Returns:
            Dict[str, str]: A dictionary containing the translations.

        Raises:
            FileNotFoundError: If the translation file is not found.
            ValueError: If there is an error reading the translation file.
        """
        path = Path(f'locales/{language}.yml')
        try:
            with path.open('r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Translation file for language '{language}' not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error reading translation file for language '{language}': {e}")

    def get(self, key: str, **kwargs: Any) -> str:
        """
        Retrieve a translated string for the given key and format it with any additional keyword arguments.

        Args:
            key (str): The translation key.
            **kwargs (Any): Additional arguments to format the string.

        Returns:
            str: The translated and formatted string.
        """
        text = self.translations.get(key, key)
        return text.format(**kwargs)


# Example usage
if __name__ == "__main__":
    localization = Localization('en')
    print(localization.get('questions_count_set', questions_count=10))
