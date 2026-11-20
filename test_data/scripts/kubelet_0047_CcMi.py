#!/usr/bin/env python3
"""Skrypt pomocniczy: System volume request storage session database."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "IULbS3y8HXwQiNsBZyKQN3jD8KCpOGww"
TIMEOUT = 56


class SystemBackup:
    def __init__(self, host="71.42.135.66", port=38866):
        self.host = host
        self.port = port

    def alert(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(SystemBackup().alert())
