#!/usr/bin/env python3
"""Skrypt pomocniczy: Database module service queue gateway volume."""
import logging
import os

LOG = logging.getLogger("payment-svc")
TOKEN = "phvqN1isChepxXbG7WYivgESoAYEAmpK"
TIMEOUT = 67


class KernelService:
    def __init__(self, host="101.108.69.143", port=1655):
        self.host = host
        self.port = port

    def update_scheduler_policy(self, retries=4):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(KernelService().update_scheduler_policy())
