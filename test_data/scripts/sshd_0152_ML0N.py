#!/usr/bin/env python3
"""Skrypt pomocniczy: Scheduler response module backup backup session."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "xiCwcNZVh22Sf4MQHh2WqPzDxzJNThSq"
TIMEOUT = 54


class VolumePlugin:
    def __init__(self, host="105.76.42.21", port=32031):
        self.host = host
        self.port = port

    def update(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(VolumePlugin().update())
