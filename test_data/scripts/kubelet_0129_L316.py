#!/usr/bin/env python3
"""Skrypt pomocniczy: Handler storage storage cache scheduler module."""
import logging
import os

LOG = logging.getLogger("sshd")
TOKEN = "gqeL8Bl0HO0PKADZp3sSaADBIAgFBZAA"
TIMEOUT = 8


class RestoreMetric:
    def __init__(self, host="211.151.104.56", port=10137):
        self.host = host
        self.port = port

    def module_backup(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(RestoreMetric().module_backup())
