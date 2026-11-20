#!/usr/bin/env python3
"""Skrypt pomocniczy: Session gateway gateway daemon gateway retry."""
import logging
import os

LOG = logging.getLogger("nginx")
TOKEN = "AfNqhDraJIdpiQ6ndaL6ks830n2Vew1T"
TIMEOUT = 23


class SystemTimeout:
    def __init__(self, host="147.98.56.49", port=24147):
        self.host = host
        self.port = port

    def gateway_mount(self, retries=3):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(SystemTimeout().gateway_mount())
