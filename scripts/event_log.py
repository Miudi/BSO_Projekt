"""
event_log.py - rejestrowanie zdarzen i bledow programu kopii zapasowych.

Zalozenia:
  * modul `logging`, poziomy INFO / WARNING / ERROR / CRITICAL,
  * format: data | poziom | modul | zdarzenie | komunikat,
  * zapis do pliku z rotacją + rownolegle na konsole,
  * filtr usuwajacy z logow klucze, hasla i inne wrazliwe dane.
"""

from __future__ import annotations

import logging
import os
import re
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(event)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 1 * 1024 * 1024     # 1 MiB na plik logu
BACKUP_COUNT = 5                # ile starych plikow logu trzymac


class Event(str, Enum):
    """Katalog zdarzen rejestrowanych przez program."""
    # zdarzenia normalne
    BACKUP_START = "BACKUP_START"
    BACKUP_OK = "BACKUP_OK"
    ENCRYPT_OK = "ENCRYPT_OK"
    CHECKSUM_OK = "CHECKSUM_OK"
    SIGN_OK = "SIGN_OK"
    ROTATION = "ROTATION"
    NO_CHANGES = "NO_CHANGES"
    VERIFY_OK = "VERIFY_OK"
    RESTORE_OK = "RESTORE_OK"
    # bledy
    KEY_MISSING = "KEY_MISSING"
    ENCRYPT_ERROR = "ENCRYPT_ERROR"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    ARCHIVE_CORRUPTED = "ARCHIVE_CORRUPTED"
    ACCESS_DENIED = "ACCESS_DENIED"
    UNEXPECTED = "UNEXPECTED"


# poziom domyslny dla kazdego zdarzenia
EVENT_LEVEL = {
    Event.BACKUP_START: logging.INFO,
    Event.BACKUP_OK: logging.INFO,
    Event.ENCRYPT_OK: logging.INFO,
    Event.CHECKSUM_OK: logging.INFO,
    Event.SIGN_OK: logging.INFO,
    Event.ROTATION: logging.INFO,
    Event.NO_CHANGES: logging.WARNING,
    Event.VERIFY_OK: logging.INFO,
    Event.RESTORE_OK: logging.INFO,
    Event.KEY_MISSING: logging.CRITICAL,
    Event.ENCRYPT_ERROR: logging.ERROR,
    Event.CHECKSUM_MISMATCH: logging.ERROR,
    Event.SIGNATURE_INVALID: logging.CRITICAL,
    Event.ARCHIVE_CORRUPTED: logging.ERROR,
    Event.ACCESS_DENIED: logging.ERROR,
    Event.UNEXPECTED: logging.CRITICAL,
}


class SensitiveDataFilter(logging.Filter):
    """Maskuje wrazliwe dane (klucze, hasla, tokeny) w komunikatach.
    Sumy kontrolne NIE sa maskowane - nie sa tajne i przydaja sie w diagnostyce."""
    PATTERNS = [
        (re.compile(r"(?i)\b(key|klucz|password|haslo|secret|token)\s*[=:]\s*\S+"),
         r"\1=***"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, repl in self.PATTERNS:
            msg = pattern.sub(repl, msg)
        record.msg, record.args = msg, None
        if not hasattr(record, "event"):
            record.event = "-"
        return True


def setup_logger(name: str = "backup", log_dir: str | Path = "logs",
                 level: int = logging.INFO, console: bool = True) -> logging.Logger:
    """Konfiguruje logger z rotacja plikow i filtrem danych wrazliwych."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(log_dir, 0o700)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    fmt = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    flt = SensitiveDataFilter()

    fh = RotatingFileHandler(log_dir / f"{name}.log", maxBytes=MAX_BYTES,
                             backupCount=BACKUP_COUNT, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.addFilter(flt)
    logger.addHandler(fh)

    if console:
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        ch.addFilter(flt)
        logger.addHandler(ch)
    return logger


def log_event(logger: logging.Logger, event: Event, message: str = "",
              level: int | None = None, exc_info: bool = False) -> None:
    """Rejestruje zdarzenie z katalogu Event z odpowiednim poziomem."""
    logger.log(level or EVENT_LEVEL[event], message, extra={"event": event.value},
               exc_info=exc_info)


def log_exception(logger: logging.Logger, exc: Exception) -> Event:
    """Mapuje wyjatek na zdarzenie, loguje go i zwraca zdarzenie."""
    from scripts.integrity import (ChecksumMismatchError, MissingKeyError,
                           SignatureError, IntegrityError)
    mapping = [
        (MissingKeyError, Event.KEY_MISSING),
        (SignatureError, Event.SIGNATURE_INVALID),
        (ChecksumMismatchError, Event.CHECKSUM_MISMATCH),
        (IntegrityError, Event.ARCHIVE_CORRUPTED),
        (PermissionError, Event.ACCESS_DENIED),
    ]
    event = next((ev for cls, ev in mapping if isinstance(exc, cls)), Event.UNEXPECTED)
    log_event(logger, event, f"{type(exc).__name__}: {exc}",
              exc_info=(event == Event.UNEXPECTED))
    return event
