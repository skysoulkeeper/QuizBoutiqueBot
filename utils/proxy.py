# MIT License
# Copyright (c) 2024 skysoulkeeper
# See LICENSE file for more details.

"""
Module: utils/proxy.py

Description:
This module provides a ProxyHandler class that facilitates the setup and
management of proxies for HTTP and SOCKS protocols. It supports proxy
authentication and includes methods for testing proxy connectivity and making
requests through the configured proxy.
"""

from typing import Optional, Dict
import requests
from .logger import LoggerFactory


class ProxyHandler:
    def __init__(self, proxy_host: str, proxy_port: int, proxy_protocol: str = 'http',
                 proxy_username: Optional[str] = None,
                 proxy_password: Optional[str] = None, config: Dict = None):
        # Initialize ProxyHandler with provided parameters
        self.logger = LoggerFactory.get_logger(config)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_protocol = proxy_protocol.lower()
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy = None

    def set_proxy(self):
        # Set up proxy based on provided parameters
        if self.proxy is not None:
            return
        credentials = ""
        if self.proxy_username and self.proxy_password:
            credentials = f"{self.proxy_username}:{self.proxy_password}@"

        if self.proxy_protocol in ['http', 'https']:
            proxy_url = f"{self.proxy_protocol}://{credentials}{self.proxy_host}:{self.proxy_port}"
            self.proxy = {self.proxy_protocol: proxy_url}
            self.logger.debug(
                f"Connecting to {self.proxy_protocol.upper()} proxy: {proxy_url}")
        elif self.proxy_protocol == 'socks':
            self.logger.debug(
                f"Connecting to SOCKS proxy: {self.proxy_host}:{self.proxy_port}, Username: {self.proxy_username}, Password: {self.proxy_password}")
            if self.proxy_username and self.proxy_password:
                self.proxy = {
                    'http': f"socks5://{credentials}{self.proxy_host}:{self.proxy_port}",
                    'https': f"socks5://{credentials}{self.proxy_host}:{self.proxy_port}"
                }
            else:
                self.proxy = {
                    'http': f"socks5://{self.proxy_host}:{self.proxy_port}",
                    'https': f"socks5://{self.proxy_host}:{self.proxy_port}"
                }
        else:
            self.logger.warning("Unsupported proxy protocol: {self.proxy_protocol}")

    def test_proxy_access(self):
        # Test proxy access by making a request to a test endpoint
        try:
            self.set_proxy()
            response = requests.get("http://httpbin.org/ip", proxies=self.proxy,
                                    timeout=10)
            if response.status_code == 200:
                self.logger.debug(
                    f"Proxy test successful, IP: {response.json()['origin']}")
                return True
            else:
                self.logger.error(
                    f"Proxy test failed with status code: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error testing proxy access: {e}")
            return False

    def make_request_through_proxy(self, url: str):
        # Make an HTTP request through the configured proxy
        try:
            self.set_proxy()
            response = requests.get(url, proxies=self.proxy, timeout=20)
            if response.status_code == 200:
                self.logger.debug("Request through proxy successful.")
                return response.text
            else:
                self.logger.error(
                    f"Error making request through proxy: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error making request through proxy: {e}")
            return None

    def _get_proxy_auth_header(self):
        # Get proxy authentication header if username and password are provided
        if self.proxy_username and self.proxy_password:
            auth_str = f"{self.proxy_username}:{self.proxy_password}"
            return "Basic " + auth_str
        return None
