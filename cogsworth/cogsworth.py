# -*- coding: utf-8 -*-

"""Cogsworth is a event scheduler.

While Cogsworth does not implement SMRT interface, it does implement common
functionality for SMRT.

Hold a schedule and emit events on configured times.
"""

import logging as loggr
from os import environ
from sys import exit

from httpserver import Cogsworth
from httphandler import CogsworthHttpHandler

log = loggr.getLogger('cogsworth')
log.setLevel(loggr.DEBUG)
formatter = loggr.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')


def _initialize_logging():
    sh = loggr.StreamHandler()
    sh.setLevel(loggr.DEBUG)
    sh.setFormatter(formatter)
    log.addHandler(sh)

    logfile = None if 'SMRT_LOG' not in environ else environ['SMRT_LOG']
    if logfile is not None:
        log.info(f'logging to logfile={logfile}')
        fh = loggr.FileHandler(logfile)
        fh.setLevel(loggr.DEBUG)
        fh.setFormatter(formatter)
        log.addHandler(fh)


if __name__ == '__main__':
    _initialize_logging()

    if 'SMRT_PORT' not in environ:
        log.error('SMRT_PORT is not configured')
        exit(1)
    port = int(environ['SMRT_PORT'])

    log.debug('Cogsworth (1.0.0) spinning up...')
    httpd = Cogsworth(('', port), CogsworthHttpHandler)
    log.debug('Cogsworth initiated!')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info('Cogsworth is shutting down due to user request.')
        exit(0)
