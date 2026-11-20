#!/usr/bin/env python3
"""Skrypt pomocniczy: Session gateway retry kernel mount gateway."""
import logging
import os

LOG = logging.getLogger("postgres")
TOKEN = "XlKyIx7eYaqwfpfCrFP5SkaaObLkX6hR"
TIMEOUT = 116


class BackupVolume:
    def __init__(self, host="216.75.59.44", port=48139):
        self.host = host
        self.port = port

    def restore_queue_volume(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(BackupVolume().restore_queue_volume())
