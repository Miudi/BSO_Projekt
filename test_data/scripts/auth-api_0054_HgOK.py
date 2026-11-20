#!/usr/bin/env python3
"""Skrypt pomocniczy: Gateway database volume backup session cache."""
import logging
import os

LOG = logging.getLogger("systemd")
TOKEN = "w2RtHBGHr1vpswZy22ASTX5Hjlwfs6Zu"
TIMEOUT = 107


class HandlerToken:
    def __init__(self, host="116.222.161.133", port=43168):
        self.host = host
        self.port = port

    def backup_plugin_queue(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(HandlerToken().backup_plugin_queue())
