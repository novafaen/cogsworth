"""Cogsworth server, implements HTTPServer."""

from http.server import HTTPServer
from typing import Optional
from time import time
from pathlib import Path
from os.path import dirname

from configuration import load_config
from scheduler import Scheduler


class Cogsworth(HTTPServer):
    """Cogsworth, implement HTTPServer."""

    def __init__(self, *args, config_path: Optional[str] = None, **kwargs):
        """Initialize Cogsworth class."""
        HTTPServer.__init__(self, *args, **kwargs)
        self._started = int(time())
        self._requests_successful = 0
        self._requests_warning = 0
        self._requests_error = 0
        self._requests_bad = 0

        if config_path is None:
            raise TypeError('Cogsworth missing 1 required keyword argument:'
                            ' \'config_path\'')

        schema_path = Path(dirname(__file__)) / 'schemas' / \
            'configuration.cogsworth.schema.json'

        config = load_config(config_path, schema_path)

        self._scheduler = Scheduler(config)
        self._scheduler.start()

    def status(self):
        """Create status obect according to SMRT interface.

        :returns: ``dict`` status object.
        """
        now = int(time())
        return {
            'smrt': {
                'smrt_version': '1.0.0',
                'app_loaded': True,
                'uptime': now - self._started
            },
            'application': {
                'name': 'Cogsworth',
                'status': 'OK',
                'version': '0.0.1'
            },
            'server_time': now,
            'status': {
                'amount_successful': self._requests_successful,
                'amount_warning': self._requests_warning,
                'amount_error': self._requests_error,
                'amount_bad': self._requests_bad,
                'amount_total': (self._requests_successful
                                 + self._requests_warning
                                 + self._requests_error
                                 + self._requests_bad)
            }
        }

    def successful_response(self):
        """Record a succesful call."""
        self._requests_successful += 1

    def create_error(self, code, error_type, description,
                     warning=False, error=False, bad=False):
        """Create error response.

        :param code: HTML Error code.
        :param error_type: Error type, typically HTTP error name.
        :param description: Detailed description what went wrong.
        :param warning: Should error be counted as a warning, default `False`.
        :param error: Should error be counted as a error, default `False`.
        :param bad: Should error be counted as a bad request, default `False`.
        :returns: SMRT return type, derived from Flask return type
        """
        if warning:
            self._requests_warning += 1
        if error:
            self._requests_error += 1
        if bad:
            self._requests_bad += 1

        body = {
            'code': code,
            'error': error_type,
            'description': description
        }

        return body
