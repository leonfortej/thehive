"""
Base Analyzer class for TheHive Cortex Analyzers.

This module provides a base class that handles common analyzer functionality:
- Input/output JSON processing
- Error handling and reporting
- Taxonomy generation
- Configuration management
- TLP/PAP validation
"""

from cortexutils.analyzer import Analyzer
import logging
import sys


class BaseAnalyzer(Analyzer):
    """
    Base class for all custom Cortex analyzers.

    This class extends cortexutils.analyzer.Analyzer and provides
    common functionality for analyzer development.

    Attributes:
        service_name (str): Name of the analyzer service
        data_type (str): Type of data being analyzed (ip, domain, mail, etc.)
        tlp (int): Traffic Light Protocol level (0-3)
        pap (int): Permissible Actions Protocol level (0-3)
    """

    def __init__(self):
        """Initialize the base analyzer."""
        super(BaseAnalyzer, self).__init__()
        self.service_name = self.get_param('config.service', None, 'Service name missing')

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the analyzer."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stderr)]
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate_tlp(self, max_tlp=2):
        """
        Validate TLP (Traffic Light Protocol) level.

        Args:
            max_tlp (int): Maximum acceptable TLP level (default: 2)

        Raises:
            Exception: If TLP exceeds maximum level
        """
        if self.tlp > max_tlp:
            self.error(f'TLP level {self.tlp} exceeds maximum allowed level {max_tlp}')

    def validate_pap(self, max_pap=2):
        """
        Validate PAP (Permissible Actions Protocol) level.

        Args:
            max_pap (int): Maximum acceptable PAP level (default: 2)

        Raises:
            Exception: If PAP exceeds maximum level
        """
        if self.pap > max_pap:
            self.error(f'PAP level {self.pap} exceeds maximum allowed level {max_pap}')

    def check_required_params(self, params):
        """
        Check if all required configuration parameters are present.

        Args:
            params (list): List of required parameter names

        Raises:
            Exception: If any required parameter is missing
        """
        for param in params:
            value = self.get_param('config.' + param, None)
            if not value:
                self.error(f'Required parameter missing: {param}')

    def build_taxonomy(self, namespace, predicate, value, level='info'):
        """
        Build a taxonomy object for TheHive.

        Args:
            namespace (str): Taxonomy namespace (e.g., analyzer name)
            predicate (str): Taxonomy predicate (e.g., 'Status', 'Score')
            value (str): Taxonomy value
            level (str): Severity level ('info', 'safe', 'suspicious', 'malicious')

        Returns:
            dict: Formatted taxonomy object
        """
        return {
            'namespace': namespace,
            'predicate': predicate,
            'value': value,
            'level': level
        }

    def summary(self, raw):
        """
        Generate summary with taxonomies from raw results.

        This method should be overridden by child classes to provide
        specific summary logic.

        Args:
            raw (dict): Raw analysis results

        Returns:
            dict: Summary with taxonomies
        """
        taxonomies = []

        # Default taxonomy - override in child classes
        if raw.get('success', False):
            taxonomies.append(
                self.build_taxonomy(
                    namespace=self.service_name,
                    predicate='Status',
                    value='Success',
                    level='info'
                )
            )
        else:
            taxonomies.append(
                self.build_taxonomy(
                    namespace=self.service_name,
                    predicate='Status',
                    value='Failed',
                    level='suspicious'
                )
            )

        return {'taxonomies': taxonomies}

    def artifacts(self, raw):
        """
        Extract artifacts from raw results.

        This method should be overridden by child classes to extract
        observables (artifacts) from analysis results.

        Args:
            raw (dict): Raw analysis results

        Returns:
            list: List of artifact dictionaries
        """
        return []

    def run(self):
        """
        Main execution method - must be implemented by child classes.

        This method should contain the core analyzer logic.

        Raises:
            NotImplementedError: If not implemented by child class
        """
        raise NotImplementedError('run() method must be implemented by child class')
