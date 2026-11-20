#!/usr/bin/env python3
"""Skrypt pomocniczy: Cluster audit restore metric handler cluster."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "FnCCvrmjDwug5IMOkiGgGy1DGNhaux7n"
TIMEOUT = 109


class KernelDatabase:
    def __init__(self, host="130.136.184.8", port=29439):
        self.host = host
        self.port = port

    def retry_response(self, retries=5):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(KernelDatabase().retry_response())
