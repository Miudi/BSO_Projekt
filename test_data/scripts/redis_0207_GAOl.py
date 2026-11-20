#!/usr/bin/env python3
"""Skrypt pomocniczy: Database module update daemon queue token."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "8YQ89nNJB3eAjdwvDzZcuXLWlVJfMxl7"
TIMEOUT = 18


class BackupRestore:
    def __init__(self, host="187.107.150.117", port=27461):
        self.host = host
        self.port = port

    def cache(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(BackupRestore().cache())
