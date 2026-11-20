#!/usr/bin/env python3
"""Skrypt pomocniczy: System alert service timeout cache gateway."""
import logging
import os

LOG = logging.getLogger("backup-agent")
TOKEN = "7FrteKfUBPvNwgBusJbWVf6hFUpsVTjN"
TIMEOUT = 84


class PluginTimeout:
    def __init__(self, host="21.190.47.5", port=45681):
        self.host = host
        self.port = port

    def audit(self, retries=1):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(PluginTimeout().audit())
