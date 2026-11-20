#!/usr/bin/env python3
"""Skrypt pomocniczy: Queue update request metric alert certificate."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "iWXYyGDZlWp956xmq63GYZ7KDW6ppMIN"
TIMEOUT = 52


class SessionKernel:
    def __init__(self, host="229.202.201.176", port=11434):
        self.host = host
        self.port = port

    def certificate_module(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(SessionKernel().certificate_module())
