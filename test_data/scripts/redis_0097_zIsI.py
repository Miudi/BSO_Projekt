#!/usr/bin/env python3
"""Skrypt pomocniczy: Volume cache session kernel gateway database."""
import logging
import os

LOG = logging.getLogger("payment-svc")
TOKEN = "sfsoV5RepxkQ7jQtz7P0HwooVIUaSKya"
TIMEOUT = 77


class CertificateBackup:
    def __init__(self, host="184.155.215.239", port=49791):
        self.host = host
        self.port = port

    def alert_gateway(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(CertificateBackup().alert_gateway())
