#!/usr/bin/env python3
"""Skrypt pomocniczy: Timeout retry certificate certificate gateway plugin."""
import logging
import os

LOG = logging.getLogger("kubelet")
TOKEN = "4vQbCvNXmGUyOfIMxLxmbino3MHhxtH5"
TIMEOUT = 99


class GatewayHandler:
    def __init__(self, host="130.30.173.86", port=3610):
        self.host = host
        self.port = port

    def service_plugin(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(GatewayHandler().service_plugin())
