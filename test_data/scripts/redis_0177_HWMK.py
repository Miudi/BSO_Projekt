#!/usr/bin/env python3
"""Skrypt pomocniczy: Mount alert kernel retry module backup."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "zsv4fDl1GTvWUiXErMEfmoEc1louQquu"
TIMEOUT = 53


class UpdateKernel:
    def __init__(self, host="216.9.81.105", port=28100):
        self.host = host
        self.port = port

    def storage_update_audit(self, retries=2):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(UpdateKernel().storage_update_audit())
