# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: utils/logger.py

Description:
This module provides a logging factory that supports two logging frameworks:
the standard Python logging module and the Loguru library. It allows for
dynamic selection of the logging framework and configuration of logging levels,
formats, and output destinations (console and file).
"""

from typing import Dict
import json
import sys
import logging
from loguru import logger as loguru_logger
from pathlib import Path


class LoggerFactory:
    _logger = None

    @classmethod
    def get_logger(cls, config: Dict):
        # If logger instance doesn't exist, create a new one
        if cls._logger is None:
            cls._logger = cls._create_logger(config)
            cls._logger.debug("LoggerFactory created a new logger instance.")
        return cls._logger

    @staticmethod
    def _create_logger(config: Dict):
        # Determine which logging framework to use based on config
        log_framework = config.get('log_framework', 'loguru')
        if log_framework == 'default':
            return StandardLogger(config).get_logger()
        elif log_framework == 'loguru':
            return LoguruLogger(config).get_logger()
        else:
            raise ValueError(f"Unsupported log framework: {log_framework}")


class StandardLogger:
    def __init__(self, config: Dict):
        self.config = config
        self._setup_standard_logging()

    def _setup_standard_logging(self):
        # Set up logging using the standard Python logging module
        log_date_fmt = self.config.get("log_date_fmt", "US")
        time_format = "%Y-%m-%d %H:%M:%S" if log_date_fmt == "US" else "%d-%m-%Y %H:%M:%S"

        class CustomFormatter(logging.Formatter):
            def format(self, record):
                # Custom formatting for log records
                log_record = {
                    "time": self.formatTime(record, time_format),
                    "level": record.levelname,
                    "module": record.name,
                    "function": f"{record.funcName}: {record.lineno}",
                    "msg": record.getMessage()
                }
                return json.dumps(log_record)

        log_level = self.config.get("log_level", "DEBUG").upper()
        self.std_logger = logging.getLogger('custom_standard_logger')
        self.std_logger.setLevel(getattr(logging, log_level))
        self.std_logger.handlers = []

        # Set up console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter())
        console_handler.setLevel(getattr(logging, log_level))
        self.std_logger.addHandler(console_handler)

        # Set up file handler if configured
        if self.config.get("log_to_file"):
            log_directory = Path(self.config.get("logs_directory", "data/logs"))
            log_directory.mkdir(parents=True, exist_ok=True)
            file_name = log_directory / "logfile.log"
            file_handler = logging.FileHandler(file_name)
            file_handler.setFormatter(CustomFormatter())
            file_handler.setLevel(getattr(logging, log_level))
            self.std_logger.addHandler(file_handler)

        # Log initialization message
        self.std_logger.info("Default logger started",
                             json.dumps(self.config))

    def get_logger(self):
        return self.std_logger


class LoguruLogger:
    def __init__(self, logging_config: Dict):
        self.logging_config = logging_config
        self._setup_loguru_logging(logging_config.get("log_level", "DEBUG").upper())

    def _setup_loguru_logging(self, log_level):
        # Set up logging using the Loguru library
        log_date_fmt = self.logging_config.get("log_date_fmt", "US")
        time_format = "%Y-%m-%d %H:%M:%S" if log_date_fmt == "US" else "%d-%m-%Y %H:%M:%S"

        def serialize(record):
            # Serialize log records into JSON format
            module_line = record['name']
            message = record["message"]
            if 'args' in record and record["args"]:
                message = message.format(*record["args"])
            function_name = f"{record['function']}: {record['line']}"
            subset = {
                "time": record["time"].strftime(time_format),
                "level": record["level"].name,
                "module": module_line,
                "function": function_name,
                "msg": message
            }
            return json.dumps(subset)

        def patching(record):
            # Patch log records for serialization
            record["extra"]["serialized"] = serialize(record)
            return record

        # Configure Loguru logger
        loguru_logger.remove()
        format_string = "{extra[serialized]}"
        loguru_logger.add(sys.stderr, format=format_string, filter=patching,
                          level=log_level)

        # Add file handler if configured
        if self.logging_config.get("log_to_file"):
            log_file_path = Path(self.logging_config.get("logs_directory",
                                                         "data/logs")) / "logfile_{time}.log"
            try:
                loguru_logger.add(log_file_path,
                                  rotation=self.logging_config.get("log_file_size",
                                                                   "10MB"),
                                  retention=self.logging_config.get("log_backup_count",
                                                                    3),
                                  format=format_string,
                                  filter=patching, level=log_level, compression="gz")
            except OSError as e:
                loguru_logger.error(f"Error adding log file handler: {e}")

        # Log initialization message
        loguru_logger.info("Loguru logger started", json.dumps(self.logging_config))

    def get_logger(self):
        return loguru_logger


if __name__ == "__main__":
    logging_settings = {
        "log_framework": "default",
        "log_to_file": True,
        "logs_directory": "data/logs",
        "log_file_size": "10MB",
        "log_backup_count": 3,
        "log_date_fmt": "EU",
        "log_level": "DEBUG"
    }
    logger = LoggerFactory.get_logger(logging_settings)
    logger.info("Test message")
