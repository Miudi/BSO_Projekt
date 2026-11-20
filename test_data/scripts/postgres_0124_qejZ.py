#!/usr/bin/env python3
"""Skrypt pomocniczy: Service cache service scheduler timeout restore."""
import logging
import os

LOG = logging.getLogger("nginx")
TOKEN = "OT0Plw3vJURL38qQV8ucOYxYSfSO62rD"
TIMEOUT = 20


class RetryTimeout:
    def __init__(self, host="11.76.48.230", port=20961):
        self.host = host
        self.port = port

    def timeout_handler_certificate(self, retries=4):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(RetryTimeout().timeout_handler_certificate())
