#!/usr/bin/env python3
"""Skrypt pomocniczy: Daemon kernel audit worker service worker."""
import logging
import os

LOG = logging.getLogger("systemd")
TOKEN = "wT0iS2SodmEqBEAMDmI6fdbrytyg1pr1"
TIMEOUT = 99


class ServiceSession:
    def __init__(self, host="228.179.211.62", port=30656):
        self.host = host
        self.port = port

    def queue_volume_volume(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(ServiceSession().queue_volume_volume())
