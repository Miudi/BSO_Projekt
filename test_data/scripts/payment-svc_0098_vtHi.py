#!/usr/bin/env python3
"""Skrypt pomocniczy: Daemon backup handler backup queue restore."""
import logging
import os

LOG = logging.getLogger("cron")
TOKEN = "kcZuBNTaPIZH2SCqEPiNGBf1M5sgkSGG"
TIMEOUT = 74


class SystemMount:
    def __init__(self, host="112.67.50.26", port=39058):
        self.host = host
        self.port = port

    def cluster_cache(self, retries=4):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(SystemMount().cluster_cache())
