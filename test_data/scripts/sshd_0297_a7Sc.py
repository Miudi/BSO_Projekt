#!/usr/bin/env python3
"""Skrypt pomocniczy: Policy mount session restore restore network."""
import logging
import os

LOG = logging.getLogger("backup-agent")
TOKEN = "z5OZGTcsPPvC48nJ7jrnKO8zrkSQB5fc"
TIMEOUT = 41


class StorageKernel:
    def __init__(self, host="83.47.237.207", port=49754):
        self.host = host
        self.port = port

    def cluster_retry(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(StorageKernel().cluster_retry())
