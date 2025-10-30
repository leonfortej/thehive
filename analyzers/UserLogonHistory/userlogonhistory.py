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
        self.api_base_url = self.get_param('config.api_url', None, 'API URL is required')
        self.api_signature = self.get_param('config.api_signature', None, 'API signature is required')
        self.timeout = self.get_param('config.timeout', 60)
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

            # Construct full API URL with signature at the end
            # The signature goes at the end as: &sig=SIGNATURE_VALUE
            api_url = f'{self.api_base_url}&sig={self.api_signature}'

            # Initialize API client
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*'
            }

            client = APIClient(
                timeout=self.timeout,
                verify_ssl=self.verify_ssl,
                headers=headers
            )

            # Prepare POST body with the required format
            post_data = {
                'dataType': 'mail',
                'data': self.email,
                'tlp': self.tlp,
                'pap': self.pap
            }

            self.logger.info(f'Making POST request to API')

            # Make POST request
            response = client.post(api_url, data=post_data)

            self.logger.info(f'Successfully retrieved logon history')

            # Process the response
            analysis_result = self._process_response(response)

            # Report results
            self.report(analysis_result)

        except Exception as e:
            self.logger.error(f'Error retrieving logon history: {str(e)}')
            self.error(f'Failed to retrieve logon history: {str(e)}')

    def _process_response(self, response):
        """
        Process API response and extract logon history analysis.

        The API returns a response with:
        - success: boolean
        - full: { report: markdown_formatted_report }
        - summary: { taxonomies: array }

        Args:
            response (dict): API response data

        Returns:
            dict: Processed analysis result for Cortex
        """
        if not isinstance(response, dict):
            self.logger.error('Unexpected response format: not a dictionary')
            return {
                'success': False,
                'error': 'Invalid response format from API'
            }

        # Extract success status
        success = response.get('success', False)

        if not success:
            self.logger.warning('API returned success=false')
            return {
                'success': False,
                'error': 'API analysis failed'
            }

        # Extract the full report
        full_data = response.get('full', {})
        markdown_report = full_data.get('report', '')

        # Parse the markdown report to extract structured data
        parsed_data = self._parse_markdown_report(markdown_report)

        # Build the result
        result = {
            'success': True,
            'email': self.email,
            'raw_report': markdown_report,
            'query_time': datetime.now(timezone.utc).isoformat()
        }

        # Add parsed data to result
        result.update(parsed_data)

        return result

    def _parse_markdown_report(self, markdown_text):
        """
        Parse the markdown report to extract structured data.

        The report contains sections like:
        - Executive Summary (with sign-in counts, IPs, locations, devices, risk level)
        - Risk Indicators
        - Geographic Distribution
        - Source IP Analysis
        - Device & Application Summary
        - Authentication Details

        Args:
            markdown_text (str): Markdown formatted report

        Returns:
            dict: Structured data extracted from the report
        """
        import re

        data = {}

        try:
            # Extract Executive Summary data
            # Total Sign-ins
            match = re.search(r'\*\*Total Sign-ins:\*\*\s*(\d+)', markdown_text)
            if match:
                data['total_signins'] = int(match.group(1))

            # Successful sign-ins
            match = re.search(r'\*\*Successful:\*\*\s*(\d+)', markdown_text)
            if match:
                data['successful_signins'] = int(match.group(1))

            # Failed sign-ins
            match = re.search(r'\*\*Failed:\*\*\s*(\d+)', markdown_text)
            if match:
                data['failed_signins'] = int(match.group(1))

            # Unique IP Addresses
            match = re.search(r'\*\*Unique IP Addresses:\*\*\s*(\d+)', markdown_text)
            if match:
                data['unique_ips'] = int(match.group(1))

            # Unique Locations
            match = re.search(r'\*\*Unique Locations:\*\*\s*(\d+)', markdown_text)
            if match:
                data['unique_locations'] = int(match.group(1))

            # Unique Devices
            match = re.search(r'\*\*Unique Devices:\*\*\s*(\d+)', markdown_text)
            if match:
                data['unique_devices'] = int(match.group(1))

            # Overall Risk Level
            match = re.search(r'\*\*Overall Risk Level:\*\*\s*(\w+)', markdown_text)
            if match:
                data['risk_level'] = match.group(1).strip()

            # Analysis Period
            match = re.search(r'\*\*Analysis Period:\*\*\s*([\d-]+)\s*to\s*([\d-]+)', markdown_text)
            if match:
                data['period_start'] = match.group(1)
                data['period_end'] = match.group(2)

            # Extract IP addresses from IP Analysis table
            # Note: The markdown may have escaped newlines (\\n) instead of actual newlines
            ip_addresses = []

            # Try to find the IP table section
            ip_section = re.search(r'\|\s*IP Address\s*\|\s*Login Count\s*\|([^#]*?)(?:##|\Z)', markdown_text, re.DOTALL | re.IGNORECASE)
            if ip_section:
                table_content = ip_section.group(1)
                # Split by both actual newlines and escaped newlines
                lines = re.split(r'\\n|\n', table_content)

                for line in lines:
                    # Skip header separator lines and empty lines
                    if not line.strip() or '---' in line:
                        continue

                    # Extract IP and count from lines with pipes
                    if '|' in line:
                        parts = [p.strip() for p in line.split('|') if p.strip()]
                        if len(parts) >= 2:
                            # Validate it looks like an IP address (has dots or colons)
                            if '.' in parts[0] or ':' in parts[0]:
                                ip_addresses.append({
                                    'ip': parts[0],
                                    'count': parts[1]
                                })

            data['ip_addresses'] = ip_addresses

            # Extract MFA usage percentage
            match = re.search(r'\*\*MFA Usage:\*\*\s*(\d+)%', markdown_text)
            if match:
                data['mfa_usage_percent'] = int(match.group(1))

            # Extract interactive vs non-interactive
            match = re.search(r'\*\*Interactive vs Non-Interactive:\*\*\s*(\d+)\s*interactive,\s*(\d+)\s*non-interactive', markdown_text)
            if match:
                data['interactive_signins'] = int(match.group(1))
                data['noninteractive_signins'] = int(match.group(2))

            # High-Risk Sign-ins
            match = re.search(r'\*\*High-Risk Sign-ins:\*\*\s*(\d+)', markdown_text)
            if match:
                data['high_risk_signins'] = int(match.group(1))

            # Geographic Distribution - extract locations
            match = re.search(r'\*\*Location\(s\):\*\*\s*([^\n]+)', markdown_text)
            if match:
                locations = [loc.strip() for loc in match.group(1).split(',')]
                data['locations'] = locations

        except Exception as e:
            self.logger.warning(f'Error parsing markdown report: {str(e)}')

        return data

    def summary(self, raw):
        """
        Generate summary with taxonomies for TheHive.

        Args:
            raw (dict): Raw analysis results

        Returns:
            dict: Summary with taxonomies
        """
        taxonomies = []
        namespace = 'LoginAnalysis'

        if raw.get('success'):
            # Taxonomy 1: Total sign-ins
            total_signins = raw.get('total_signins', 0)
            if total_signins:
                taxonomies.append(
                    self.build_taxonomy(
                        namespace=namespace,
                        predicate='SignIns',
                        value=str(total_signins),
                        level='info'
                    )
                )

            # Taxonomy 2: Failed sign-ins
            failed_signins = raw.get('failed_signins', 0)
            if failed_signins:
                level = 'suspicious' if failed_signins > 5 else 'info'
                taxonomies.append(
                    self.build_taxonomy(
                        namespace=namespace,
                        predicate='Failed',
                        value=str(failed_signins),
                        level=level
                    )
                )

            # Taxonomy 3: Risk Level (from API analysis)
            risk_level = raw.get('risk_level', 'Unknown')
            taxonomies.append(
                self.build_taxonomy(
                    namespace=namespace,
                    predicate='RiskLevel',
                    value=risk_level,
                    level=self._get_taxonomy_level(risk_level)
                )
            )

            # Taxonomy 4: MFA Usage
            mfa_percent = raw.get('mfa_usage_percent')
            if mfa_percent is not None:
                level = 'safe' if mfa_percent >= 90 else ('suspicious' if mfa_percent < 50 else 'info')
                taxonomies.append(
                    self.build_taxonomy(
                        namespace=namespace,
                        predicate='MFA',
                        value=f'{mfa_percent}%',
                        level=level
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

        Extracts IP addresses from the login analysis report.

        Args:
            raw (dict): Raw analysis results

        Returns:
            list: List of artifacts
        """
        artifacts = []

        if not raw.get('success'):
            return artifacts

        # Extract IP addresses from parsed data
        ip_addresses = raw.get('ip_addresses', [])

        for ip_entry in ip_addresses:
            ip_addr = ip_entry.get('ip', '').strip()
            login_count = ip_entry.get('count', '0')

            # Skip empty or invalid IPs
            if not ip_addr or ip_addr == '':
                continue

            # IPv6 addresses start with numbers or letters followed by colon
            # IPv4 addresses are dotted decimal
            artifacts.append({
                'dataType': 'ip',
                'data': ip_addr,
                'message': f'IP address from logon history ({login_count} logins) for {raw.get("email")}'
            })

        return artifacts


if __name__ == '__main__':
    """Main entry point for the analyzer."""
    UserLogonHistoryAnalyzer().run()
