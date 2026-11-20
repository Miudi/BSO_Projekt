#!/usr/bin/env python3
"""Skrypt pomocniczy: Response mount daemon restore policy audit."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "HyvSqBwDj6hcVPwreKq30jpMjfUM6zyw"
TIMEOUT = 24


class VolumeTimeout:
    def __init__(self, host="52.12.106.127", port=27028):
        self.host = host
        self.port = port

    def volume_plugin_service(self, retries=4):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(VolumeTimeout().volume_plugin_service())
