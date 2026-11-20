#!/usr/bin/env python3
"""Skrypt pomocniczy: Timeout certificate cluster response response module."""
import logging
import os

LOG = logging.getLogger("redis")
TOKEN = "TbYFmBaFEG1FhotCVYqSjWae15LnRQOL"
TIMEOUT = 68


class RetryScheduler:
    def __init__(self, host="216.127.190.167", port=28836):
        self.host = host
        self.port = port

    def session_scheduler_database(self, retries=1):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(RetryScheduler().session_scheduler_database())
