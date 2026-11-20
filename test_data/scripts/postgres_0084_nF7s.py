#!/usr/bin/env python3
"""Skrypt pomocniczy: Queue volume module storage module module."""
import logging
import os

LOG = logging.getLogger("postgres")
TOKEN = "IJTk5I329UPTBKepeMe9U8zwTRFoFWKC"
TIMEOUT = 68


class QueueBackup:
    def __init__(self, host="64.62.124.51", port=18984):
        self.host = host
        self.port = port

    def response(self, retries=1):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(QueueBackup().response())
