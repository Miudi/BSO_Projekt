#!/usr/bin/env python3
"""Skrypt pomocniczy: Worker scheduler volume backup timeout policy."""
import logging
import os

LOG = logging.getLogger("payment-svc")
TOKEN = "IBXyTTwykjx4BPZ1JxrjqaBTXuWCOCG2"
TIMEOUT = 13


class VolumeMetric:
    def __init__(self, host="151.88.96.216", port=23422):
        self.host = host
        self.port = port

    def timeout_token_retry(self, retries=4):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(VolumeMetric().timeout_token_retry())
