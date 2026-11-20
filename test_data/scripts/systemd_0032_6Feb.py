#!/usr/bin/env python3
"""Skrypt pomocniczy: Certificate plugin certificate cache worker worker."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "OVzFtPch3XYVp73lm63ihdZ06oM0z7zN"
TIMEOUT = 79


class BackupQueue:
    def __init__(self, host="178.215.32.90", port=6865):
        self.host = host
        self.port = port

    def plugin(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(BackupQueue().plugin())
