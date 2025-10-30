"""
Utility classes and functions for Cortex analyzers and responders.

This module provides reusable components:
- APIClient: HTTP client for REST API calls
- DataValidator: Input data validation utilities
"""

import requests
import json
import re
from typing import Dict, Any, Optional, List
import logging


class APIClient:
    """
    HTTP client for making REST API calls.

    This class provides a standardized interface for making API requests
    with proper error handling, timeout management, and response parsing.

    Attributes:
        base_url (str): Base URL for API endpoints
        timeout (int): Request timeout in seconds
        verify_ssl (bool): Whether to verify SSL certificates
        headers (dict): Default HTTP headers
    """

    def __init__(self, base_url: str = None, timeout: int = 30, verify_ssl: bool = True, headers: Dict[str, str] = None):
        """
        Initialize API client.

        Args:
            base_url (str): Base URL for API endpoints
            timeout (int): Request timeout in seconds (default: 30)
            verify_ssl (bool): Whether to verify SSL certificates (default: True)
            headers (dict): Default HTTP headers
        """
        self.base_url = base_url
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = headers or {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, endpoint: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint (str): API endpoint (will be appended to base_url if set)
            params (dict): Query parameters
            headers (dict): Additional headers (merged with default headers)

        Returns:
            dict: JSON response

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = self._merge_headers(headers)

        self.logger.info(f'GET request to: {url}')

        try:
            response = requests.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            self.logger.error(f'Request timeout: {url}')
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Request failed: {str(e)}')
            raise

    def post(self, endpoint: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint (str): API endpoint (will be appended to base_url if set)
            data (dict): Request body data
            headers (dict): Additional headers (merged with default headers)

        Returns:
            dict: JSON response

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self._build_url(endpoint)
        request_headers = self._merge_headers(headers)

        self.logger.info(f'POST request to: {url}')

        try:
            response = requests.post(
                url,
                json=data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            self.logger.error(f'Request timeout: {url}')
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Request failed: {str(e)}')
            raise

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from base_url and endpoint.

        Args:
            endpoint (str): API endpoint

        Returns:
            str: Full URL
        """
        if self.base_url:
            # Remove trailing slash from base_url and leading slash from endpoint
            base = self.base_url.rstrip('/')
            path = endpoint.lstrip('/')
            return f'{base}/{path}'
        return endpoint

    def _merge_headers(self, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        Merge default headers with additional headers.

        Args:
            additional_headers (dict): Additional headers to merge

        Returns:
            dict: Merged headers
        """
        merged = self.headers.copy()
        if additional_headers:
            merged.update(additional_headers)
        return merged


class DataValidator:
    """
    Utility class for validating input data.

    This class provides methods to validate common data types
    used in Cortex analyzers and responders.
    """

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email (str): Email address to validate

        Returns:
            bool: True if valid email format, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Validate IP address format (IPv4).

        Args:
            ip (str): IP address to validate

        Returns:
            bool: True if valid IPv4 format, False otherwise
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False

        # Check each octet is 0-255
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)

    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """
        Validate domain name format.

        Args:
            domain (str): Domain name to validate

        Returns:
            bool: True if valid domain format, False otherwise
        """
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if valid URL format, False otherwise
        """
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url, re.IGNORECASE))

    @staticmethod
    def is_valid_hash(hash_value: str, hash_type: str = 'md5') -> bool:
        """
        Validate hash format.

        Args:
            hash_value (str): Hash to validate
            hash_type (str): Type of hash ('md5', 'sha1', 'sha256')

        Returns:
            bool: True if valid hash format, False otherwise
        """
        hash_lengths = {
            'md5': 32,
            'sha1': 40,
            'sha256': 64
        }

        expected_length = hash_lengths.get(hash_type.lower())
        if not expected_length:
            return False

        pattern = f'^[a-fA-F0-9]{{{expected_length}}}$'
        return bool(re.match(pattern, hash_value))

    @staticmethod
    def sanitize_string(text: str) -> str:
        """
        Sanitize string input by removing potentially harmful characters.

        Args:
            text (str): Text to sanitize

        Returns:
            str: Sanitized text
        """
        # Remove control characters but keep newlines and tabs
        sanitized = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        return sanitized.strip()
