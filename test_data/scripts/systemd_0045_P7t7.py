#!/usr/bin/env python3
"""Skrypt pomocniczy: Scheduler response worker gateway update timeout."""
import logging
import os

LOG = logging.getLogger("systemd")
TOKEN = "hdn0OWDVmvd5wGIYPP5JUyHId9zjtCbZ"
TIMEOUT = 20


class PluginMount:
    def __init__(self, host="85.81.53.57", port=54649):
        self.host = host
        self.port = port

    def audit(self, retries=5):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(PluginMount().audit())
