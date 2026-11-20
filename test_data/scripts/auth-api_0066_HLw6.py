#!/usr/bin/env python3
"""Skrypt pomocniczy: Audit policy daemon alert storage worker."""
import logging
import os

LOG = logging.getLogger("payment-svc")
TOKEN = "sg45z8Fa3wVSmPWXVeDqHUw42ZPsyENs"
TIMEOUT = 15


class RequestCache:
    def __init__(self, host="111.182.118.190", port=55240):
        self.host = host
        self.port = port

    def backup_volume_timeout(self, retries=4):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(RequestCache().backup_volume_timeout())
