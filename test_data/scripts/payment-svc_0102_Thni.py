#!/usr/bin/env python3
"""Skrypt pomocniczy: Request timeout metric cluster storage backup."""
import logging
import os

LOG = logging.getLogger("postgres")
TOKEN = "EIjKRKEgGRmJ8NxP1IMB0JcMIROZZ7Bp"
TIMEOUT = 100


class TokenScheduler:
    def __init__(self, host="108.140.233.197", port=24424):
        self.host = host
        self.port = port

    def worker_database(self, retries=5):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(TokenScheduler().worker_database())
