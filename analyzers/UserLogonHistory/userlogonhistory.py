#!/usr/bin/env python3
"""
User Logon History Analyzer for TheHive Cortex.

Retrieves user logon history from Azure Logic App and formats
results for TheHive with taxonomies and artifacts.

Author: Brightspeed CIRT Team
License: AGPL-V3
Version: 1.0.0
"""

import sys
import os

# Add common module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.base_analyzer import BaseAnalyzer
from common.utils import APIClient, DataValidator


class UserLogonHistoryAnalyzer(BaseAnalyzer):
    """
    Analyzer to retrieve user logon history from Azure Logic App.

    Queries Microsoft Sentinel via Logic App to retrieve 7-day
    authentication history including sign-ins, failures, IPs,
    locations, devices, and risk assessment.
    """

    def __init__(self):
        """Initialize analyzer and validate configuration."""
        super(UserLogonHistoryAnalyzer, self).__init__()

        # Validate TLP - AMBER max (don't share with external entities)
        self.validate_tlp(max_tlp=2)

        # Get configuration
        self.api_url = self.get_param('config.api_url', None, 'API URL is required')
        self.api_signature = self.get_param('config.api_signature', None, 'API signature is required')
        self.timeout = self.get_param('config.timeout', 60)
        self.verify_ssl = self.get_param('config.verify_ssl', True)

        # Get and validate email
        self.email = self.get_data()
        validator = DataValidator()
        if not validator.is_valid_email(self.email):
            self.error(f'Invalid email format: {self.email}')

        self.logger.info(f'Initialized for email: {self.email}')

    def run(self):
        """
        Main execution method.

        Calls Logic App, validates response, and reports data to Cortex.
        The framework automatically calls summary() and artifacts().
        """
        try:
            self.logger.info(f'Retrieving logon history for: {self.email}')

            # Build API URL with signature
            api_url = f'{self.api_url}&sig={self.api_signature}'

            # Initialize HTTP client
            client = APIClient(
                timeout=self.timeout,
                verify_ssl=self.verify_ssl,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            # Prepare request body
            request_body = {
                'dataType': 'mail',
                'data': self.email,
                'tlp': self.tlp,
                'pap': self.pap
            }

            # Call Logic App
            self.logger.info('Calling Logic App API...')
            response = client.post(api_url, data=request_body)

            # Validate response format
            if not isinstance(response, dict):
                self.error('Invalid response format from Logic App')

            # Logic App returns: {success: true, full: {...}, summary: {...}, artifacts: [...]}
            # We need to extract just the "full" data portion
            if not response.get('success', False):
                error_msg = response.get('error', 'Unknown error from Logic App')
                self.error(f'Logic App analysis failed: {error_msg}')

            if 'full' not in response:
                self.error('Logic App response missing "full" data field')

            # Extract the analysis data (not the wrapper)
            analysis_data = response['full']

            self.logger.info(f'Received analysis data with keys: {list(analysis_data.keys())}')

            # Report the data - framework will call summary() and artifacts() automatically
            self.report(analysis_data)

        except Exception as e:
            self.logger.error(f'Error during analysis: {str(e)}')
            self.error(f'Failed to retrieve logon history: {str(e)}')

    def summary(self, raw):
        """
        Build taxonomies from analysis data.

        Called automatically by the cortexutils framework.
        Extracts key metrics and builds colored taxonomy cards.

        Args:
            raw (dict): Analysis data from Logic App

        Returns:
            dict: {'taxonomies': [...]} with 10 taxonomy objects
        """
        taxonomies = []

        try:
            # Extract metrics from analysis data
            account = raw.get('account', 'Unknown')
            risk_level = raw.get('risk_assessment', {}).get('overall_risk_level', 'Unknown')
            metrics = raw.get('summary_metrics', {})
            auth = raw.get('authentication_details', {})

            # Build taxonomies with appropriate colors
            # 1. Account (info - blue)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'Account', str(account), 'info')
            )

            # 2. Risk Level (color based on risk)
            risk_colors = {'High': 'malicious', 'Medium': 'suspicious', 'Low': 'safe'}
            risk_color = risk_colors.get(risk_level, 'info')
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'RiskLevel', risk_level, risk_color)
            )

            # 3. Total Sign-ins (info - blue)
            total = metrics.get('total_signins', 0)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'TotalSignins', str(total), 'info')
            )

            # 4. Successful Sign-ins (safe - green)
            successful = metrics.get('successful_signins', 0)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'SuccessfulSignins', str(successful), 'safe')
            )

            # 5. Failed Sign-ins (color based on count)
            failed = metrics.get('failed_signins', 0)
            if failed > 5:
                failed_color = 'malicious'
            elif failed > 0:
                failed_color = 'suspicious'
            else:
                failed_color = 'safe'
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'FailedSignins', str(failed), failed_color)
            )

            # 6. Unique IPs (info - blue)
            unique_ips = metrics.get('unique_ip_addresses', 0)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'UniqueIPs', str(unique_ips), 'info')
            )

            # 7. Unique Locations (info - blue)
            unique_locations = metrics.get('unique_locations', 0)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'UniqueLocations', str(unique_locations), 'info')
            )

            # 8. Unique Devices (info - blue)
            unique_devices = metrics.get('unique_devices', 0)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'UniqueDevices', str(unique_devices), 'info')
            )

            # 9. MFA Usage (safe - green)
            mfa_usage = auth.get('mfa_usage_percentage', 0)
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'MFAUsage', f'{mfa_usage}%', 'safe')
            )

            # 10. High Risk Sign-ins (color based on count)
            high_risk = auth.get('high_risk_signins', 0)
            high_risk_color = 'malicious' if high_risk > 0 else 'safe'
            taxonomies.append(
                self.build_taxonomy('UserLoginAnalysis', 'HighRiskSignins', str(high_risk), high_risk_color)
            )

            self.logger.info(f'Built {len(taxonomies)} taxonomies')

        except Exception as e:
            self.logger.error(f'Error building taxonomies: {str(e)}')
            # Fallback - return error taxonomy
            taxonomies = [
                self.build_taxonomy('UserLoginAnalysis', 'Status', 'Error', 'suspicious')
            ]

        # Return ONLY taxonomies - no debug fields!
        return {'taxonomies': taxonomies}

    def artifacts(self, raw):
        """
        Extract IP artifacts from analysis data.

        Called automatically by the cortexutils framework.
        Extracts IP addresses from login history for further investigation.

        Args:
            raw (dict): Analysis data from Logic App

        Returns:
            list: List of artifact dictionaries
        """
        artifacts = []

        try:
            ip_analysis = raw.get('ip_address_analysis', [])
            account = raw.get('account', 'Unknown')

            for ip_entry in ip_analysis:
                # IP analysis format: [[ip, count], ...]
                if isinstance(ip_entry, list) and len(ip_entry) >= 2:
                    ip_addr = str(ip_entry[0])
                    login_count = ip_entry[1]

                    artifacts.append({
                        'dataType': 'ip',
                        'data': ip_addr,
                        'message': f'Logon source for {account} ({login_count} logins)'
                    })

            if artifacts:
                self.logger.info(f'Extracted {len(artifacts)} IP artifacts')

        except Exception as e:
            self.logger.error(f'Error extracting artifacts: {str(e)}')

        return artifacts


if __name__ == '__main__':
    """Entry point - runs the analyzer."""
    UserLogonHistoryAnalyzer().run()
