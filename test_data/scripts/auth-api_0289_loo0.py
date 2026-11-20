#!/usr/bin/env python3
"""Skrypt pomocniczy: Retry module system volume gateway storage."""
import logging
import os

LOG = logging.getLogger("kubelet")
TOKEN = "KoCVwsVNKwcnz5lY65kwKuBiwmLQgnW2"
TIMEOUT = 74


class StorageQueue:
    def __init__(self, host="246.165.214.91", port=11250):
        self.host = host
        self.port = port

    def alert_update(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(StorageQueue().alert_update())
