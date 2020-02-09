"""Cogsworth HTTP Handler, implements BaseHTTPRequestHandler."""

from http.server import BaseHTTPRequestHandler
from json import dumps
import logging as loggr
from time import time

# constants
CONTENT_TYPE_ERROR = 'application/se.novafaen.smrt.error.v1+json'
CONTENT_TYPE_STATUS = 'application/se.novafaen.smrt.status.v1+json'

log = loggr.getLogger('cogsworth')


class UnsupportedMediaType(Exception):
    """Exception wrapper to handle http errors."""

    def __init__(self, *args, **kwargs):
        """Initialize UnsupportedMediaType class."""
        Exception.__init__(self, *args, *kwargs)


class NotAcceptable(Exception):
    """Exception wrapper to handle http errors."""

    def __init__(self, *args, **kwargs):
        """Initialize NotAcceptable class."""
        Exception.__init__(self, *args, *kwargs)


class CogsworthHttpHandler(BaseHTTPRequestHandler):
    """CogsworthHttpHandler implements BaseHTTPRequestHandler."""

    def __init__(self, *args, **kwargs):
        """Initialize CogsworthHttpHandler class."""
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
        self._requests_successful = 0
        self._requests_warning = 0
        self._requests_error = 0
        self._requests_bad = 0

    def do_GET(self):
        """Handle GET requests."""
        self._start = int(round(time() * 1000))  # start timer

        try:
            self._route_get()
        except UnsupportedMediaType:
            self._create_unsupported_media_type()
        except NotAcceptable:
            self._create_not_acceptable()
        except Exception as err:
            log.error('Unhandled exception: %s', err, exc_info=True)
            self._create_internal_server_error()

    def _route_get(self):
        """Route HTTP GET call."""
        if self.path == '/status':
            self._create_status()
        else:
            self._create_method_not_allowed()

    def _create_status(self):
        """Create status response, according to SMRT interface."""
        if self.headers['Accept'] != CONTENT_TYPE_STATUS:
            raise NotAcceptable()

        body = self.server.status()
        self._write_response(
            200, body,
            content_type='application/se.novafaen.smrt.status.v1+json'
        )
        self.server.successful_response()

    def _create_method_not_allowed(self):
        """Create HTTP error Method Not Allowed."""
        body = self.server.create_error(
            405, 'Method Not Allowed',
            f'No method \'{self.path}\' exist.',
            bad=True)
        self._write_response(405, body, content_type=CONTENT_TYPE_ERROR)

    def _create_not_acceptable(self):
        """Create HTTP error Not Acceptable."""
        body = self.server.create_error(
            406, 'Unsupported Media Type',
            'Invalid Content-Type header.',
            bad=True)
        self._write_response(406, body, content_type=CONTENT_TYPE_ERROR)

    def _create_unsupported_media_type(self):
        """Create HTTP error Unsupported Media Type."""
        body = self.server.create_error(
            415,
            'Not Acceptable', 'Invalid Accept header.',
            bad=True)
        self._write_response(415, body, content_type=CONTENT_TYPE_ERROR)

    def _create_internal_server_error(self):
        """Create HTTP error Internal Server Error."""
        body = self.server.create_error(
            500, 'Internal Server Error',
            'An unexpected error has occurred.',
            error=True
        )
        self._write_response(500, body, content_type=CONTENT_TYPE_ERROR)

    def _write_response(self, code, body, content_type=None):
        """Write reponse to caller.

        :param code: ``int`` http status code.
        :param body: ``dict`` http body.
        :param content_type: ``string`` optional content type.
        """
        self.send_response(code)
        if content_type is not None:
            self.send_header('Content-type', content_type)
            self.end_headers()
        self.wfile.write(bytes(dumps(body), 'UTF-8'))

        end = int(round(time() * 1000))  # stop timer
        log.debug('%s executed in %s ms',
                  self.path, end - self._start)

    def log_message(self, *args, **kwargs):
        """Overwrite handler log."""
        pass  # omit handler log
