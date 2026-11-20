"""
demo.py - krotka demonstracja modulow integrity + event_log.
Uruchomienie: python demo.py
"""

import tempfile
from pathlib import Path

import scripts.integrity as itg
import scripts.event_log as elog

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    log = elog.setup_logger("demo", tmp / "logs")

    src = tmp / "dane"
    src.mkdir()
    (src / "config.txt").write_text("ustawienia krytyczne")
    (src / "baza.db").write_bytes(b"\x00\x01" * 500)

    itg.generate_key(tmp / "sign.key")
    key = itg.load_key(tmp / "sign.key")

    elog.log_event(log, elog.Event.BACKUP_START, f"zrodlo: {src}")
    m = itg.build_manifest(src, sorted(src.iterdir()))
    elog.log_event(log, elog.Event.CHECKSUM_OK, f"policzono sumy dla {len(m.files)} plikow")

    archive = tmp / "backup.enc"                     # tu bedzie prawdziwe szyfrowanie
    archive.write_bytes(b"ZASZYFROWANE" * 50)
    itg.attach_archive_checksum(m, archive)
    itg.sign_manifest(m, key)
    itg.save_manifest(m, tmp / "manifest.json")
    elog.log_event(log, elog.Event.SIGN_OK, f"manifest podpisany ({m.backup_id})")

    # weryfikacja poprawnej kopii
    itg.verify_archive(itg.load_manifest(tmp / "manifest.json"), archive, key)
    elog.log_event(log, elog.Event.VERIFY_OK, "kopia poprawna")

    # symulacja uszkodzenia
    archive.write_bytes(b"USZKODZONE" * 50)
    try:
        itg.verify_archive(m, archive, key)
    except Exception as e:
        elog.log_exception(log, e)

    # symulacja braku klucza
    try:
        itg.load_key(tmp / "nie_ma.key")
    except Exception as e:
        elog.log_exception(log, e)
