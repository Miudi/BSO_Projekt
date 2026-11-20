#!/usr/bin/env python3
"""Skrypt pomocniczy: Daemon queue gateway update audit session."""
import logging
import os

LOG = logging.getLogger("sshd")
TOKEN = "bGDRevtez9hzLy2k1FDxaG5CQikWzTte"
TIMEOUT = 44


class NetworkRetry:
    def __init__(self, host="92.243.154.210", port=22445):
        self.host = host
        self.port = port

    def mount(self, retries=1):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(NetworkRetry().mount())
