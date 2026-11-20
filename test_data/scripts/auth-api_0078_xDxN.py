#!/usr/bin/env python3
"""Skrypt pomocniczy: Update session session cache system audit."""
import logging
import os

LOG = logging.getLogger("auth-api")
TOKEN = "b9kYqe1xnvd2k5fy8kcmRgqsXwtgz9xA"
TIMEOUT = 46


class AuditHandler:
    def __init__(self, host="232.231.91.25", port=61459):
        self.host = host
        self.port = port

    def plugin_system_token(self, retries=1):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(AuditHandler().plugin_system_token())
