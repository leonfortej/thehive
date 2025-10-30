#!/usr/bin/env python3
"""
User Logon History Analyzer for TheHive Cortex.

This analyzer retrieves user logon history from a REST API endpoint.
It accepts an email address as input and queries the configured API
to retrieve the user's authentication history.

Author: TheHive Development Team
License: AGPL-V3
"""

import sys
import os
from datetime import datetime, timezone

# Add common module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base_analyzer import BaseAnalyzer
from common.utils import APIClient, DataValidator


class UserLogonHistoryAnalyzer(BaseAnalyzer):
    """
    Analyzer to retrieve user logon history from REST API.

    This analyzer takes a user email address and queries a REST API
    endpoint to retrieve the user's logon history including timestamps,
    IP addresses, locations, and authentication status.
    """

    def __init__(self):
        """Initialize the analyzer."""
        super(UserLogonHistoryAnalyzer, self).__init__()

        # Validate TLP - don't allow sharing with external entities
        self.validate_tlp(max_tlp=2)

        # Get configuration parameters
        self.api_url = self.get_param('config.api_url', None, 'API URL is required')
        self.api_key = self.get_param('config.api_key', None)  # Optional API key
        self.timeout = self.get_param('config.timeout', 30)
        self.verify_ssl = self.get_param('config.verify_ssl', True)

        # Get the email from the observable data
        self.email = self.get_data()

        # Validate email format
        validator = DataValidator()
        if not validator.is_valid_email(self.email):
            self.error(f'Invalid email format: {self.email}')

        self.logger.info(f'Initialized UserLogonHistory analyzer for email: {self.email}')

    def run(self):
        """
        Execute the analyzer logic.

        This method:
        1. Validates input parameters
        2. Calls the REST API to retrieve logon history
        3. Processes the response
        4. Reports the results to Cortex
        """
        try:
            self.logger.info(f'Retrieving logon history for: {self.email}')

            # Initialize API client
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # Add API key to headers if provided
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            client = APIClient(
                timeout=self.timeout,
                verify_ssl=self.verify_ssl,
                headers=headers
            )

            # Make API request
            # The API URL should be the full endpoint URL
            params = {'email': self.email}

            response = client.get(self.api_url, params=params)

            self.logger.info(f'Successfully retrieved logon history')

            # Process the response
            logon_history = self._process_response(response)

            # Report results
            self.report({
                'success': True,
                'email': self.email,
                'logon_count': len(logon_history),
                'logon_history': logon_history,
                'query_time': datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            self.logger.error(f'Error retrieving logon history: {str(e)}')
            self.error(f'Failed to retrieve logon history: {str(e)}')

    def _process_response(self, response):
        """
        Process API response and extract logon history.

        This method processes the API response and extracts relevant
        logon history information. Adapt this method based on your
        actual API response structure.

        Args:
            response (dict): API response data

        Returns:
            list: Processed logon history records
        """
        logon_history = []

        # Adapt this based on your API response structure
        # Example structures handled:

        # Case 1: Response has a 'data' field with array of logons
        if 'data' in response:
            raw_data = response['data']
        # Case 2: Response has 'logons' field
        elif 'logons' in response:
            raw_data = response['logons']
        # Case 3: Response has 'events' field
        elif 'events' in response:
            raw_data = response['events']
        # Case 4: Response is directly an array
        elif isinstance(response, list):
            raw_data = response
        # Case 5: Response has 'results' field
        elif 'results' in response:
            raw_data = response['results']
        else:
            self.logger.warning('Unknown API response structure, returning raw response')
            return [response]

        # Process each logon record
        for record in raw_data:
            try:
                logon_entry = {
                    'timestamp': record.get('timestamp') or record.get('login_time') or record.get('datetime'),
                    'ip_address': record.get('ip_address') or record.get('ip') or record.get('source_ip'),
                    'location': record.get('location') or record.get('geo_location'),
                    'status': record.get('status') or record.get('result') or 'unknown',
                    'device': record.get('device') or record.get('user_agent'),
                    'city': record.get('city'),
                    'country': record.get('country'),
                    'raw_data': record  # Keep raw data for reference
                }

                # Only include fields that have values
                logon_entry = {k: v for k, v in logon_entry.items() if v is not None}

                logon_history.append(logon_entry)

            except Exception as e:
                self.logger.warning(f'Error processing logon record: {str(e)}')
                # Include the problematic record with error note
                logon_history.append({
                    'error': f'Failed to process: {str(e)}',
                    'raw_data': record
                })

        return logon_history

    def summary(self, raw):
        """
        Generate summary with taxonomies for TheHive.

        Args:
            raw (dict): Raw analysis results

        Returns:
            dict: Summary with taxonomies
        """
        taxonomies = []
        namespace = 'UserLogonHistory'

        if raw.get('success'):
            logon_count = raw.get('logon_count', 0)

            # Taxonomy 1: Logon count
            taxonomies.append(
                self.build_taxonomy(
                    namespace=namespace,
                    predicate='LogonCount',
                    value=str(logon_count),
                    level='info'
                )
            )

            # Taxonomy 2: Status
            taxonomies.append(
                self.build_taxonomy(
                    namespace=namespace,
                    predicate='Status',
                    value='Retrieved',
                    level='safe'
                )
            )

            # Taxonomy 3: Risk assessment based on patterns
            risk_level = self._assess_risk(raw.get('logon_history', []))
            taxonomies.append(
                self.build_taxonomy(
                    namespace=namespace,
                    predicate='RiskLevel',
                    value=risk_level,
                    level=self._get_taxonomy_level(risk_level)
                )
            )

        else:
            taxonomies.append(
                self.build_taxonomy(
                    namespace=namespace,
                    predicate='Status',
                    value='Failed',
                    level='suspicious'
                )
            )

        return {'taxonomies': taxonomies}

    def _assess_risk(self, logon_history):
        """
        Assess risk level based on logon patterns.

        This is a simple risk assessment. Enhance based on your requirements.

        Args:
            logon_history (list): List of logon records

        Returns:
            str: Risk level (Low, Medium, High)
        """
        if not logon_history:
            return 'Unknown'

        # Count failed logons
        failed_count = sum(
            1 for entry in logon_history
            if entry.get('status', '').lower() in ['failed', 'failure', 'denied']
        )

        # Get unique IP addresses
        ip_addresses = set(
            entry.get('ip_address')
            for entry in logon_history
            if entry.get('ip_address')
        )

        # Get unique countries
        countries = set(
            entry.get('country')
            for entry in logon_history
            if entry.get('country')
        )

        # Simple risk assessment
        if failed_count > 5:
            return 'High'
        elif failed_count > 2 or len(countries) > 3:
            return 'Medium'
        else:
            return 'Low'

    def _get_taxonomy_level(self, risk_level):
        """
        Convert risk level to taxonomy level.

        Args:
            risk_level (str): Risk level

        Returns:
            str: Taxonomy level
        """
        mapping = {
            'Low': 'safe',
            'Medium': 'suspicious',
            'High': 'malicious',
            'Unknown': 'info'
        }
        return mapping.get(risk_level, 'info')

    def artifacts(self, raw):
        """
        Extract artifacts (observables) from the results.

        Args:
            raw (dict): Raw analysis results

        Returns:
            list: List of artifacts
        """
        artifacts = []

        if not raw.get('success'):
            return artifacts

        logon_history = raw.get('logon_history', [])

        # Extract unique IP addresses as artifacts
        seen_ips = set()
        for entry in logon_history:
            ip_address = entry.get('ip_address')
            if ip_address and ip_address not in seen_ips:
                artifacts.append({
                    'dataType': 'ip',
                    'data': ip_address,
                    'message': f'IP address from logon history for {raw.get("email")}'
                })
                seen_ips.add(ip_address)

        return artifacts


if __name__ == '__main__':
    """Main entry point for the analyzer."""
    UserLogonHistoryAnalyzer().run()
