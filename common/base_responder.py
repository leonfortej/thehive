"""
Base Responder class for TheHive Cortex Responders.

This module provides a base class that handles common responder functionality:
- Input/output JSON processing
- Error handling and reporting
- Operation status reporting
- Configuration management
"""

from cortexutils.responder import Responder
import logging
import sys


class BaseResponder(Responder):
    """
    Base class for all custom Cortex responders.

    This class extends cortexutils.responder.Responder and provides
    common functionality for responder development.

    Attributes:
        service_name (str): Name of the responder service
    """

    def __init__(self):
        """Initialize the base responder."""
        super(BaseResponder, self).__init__()
        self.service_name = self.get_param('config.service', None, 'Service name missing')

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the responder."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stderr)]
        )
        self.logger = logging.getLogger(self.__class__.__name__)

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

    def operations(self, raw):
        """
        Define operations performed by the responder.

        This method should be overridden by child classes to provide
        specific operation details.

        Args:
            raw (dict): Raw execution results

        Returns:
            list: List of operation dictionaries
        """
        return []

    def run(self):
        """
        Main execution method - must be implemented by child classes.

        This method should contain the core responder logic.

        Raises:
            NotImplementedError: If not implemented by child class
        """
        raise NotImplementedError('run() method must be implemented by child class')
