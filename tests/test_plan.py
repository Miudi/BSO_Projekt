"""
test_plan.py - plan testow w postaci szkieletu testow pytest.

Uruchomienie:  python -m pytest -v tests/
Testy oznaczone `skip` czekaja na moduly z kolejnego etapu (19.12)
- szyfrowanie/odtwarzanie i rotacje.

Scenariusze (ID | opis | oczekiwany wynik):
  T01 | suma kontrolna pliku                  | zgodna z hashlib
  T02 | manifest dla zestawu plikow            | wszystkie pliki w manifescie
  T03 | poprawny podpis manifestu              | weryfikacja OK
  T04 | zmodyfikowany manifest                 | SignatureError
  T05 | zly klucz                              | SignatureError
  T06 | brak pliku klucza                      | MissingKeyError
  T07 | uszkodzone archiwum (1 bajt zmieniony) | ChecksumMismatchError
  T08 | odtworzone pliki zgodne z oryginalem   | brak problemow
  T09 | brak zmian między kopiami              | pusta lista zmian
  T10 | logi nie zawieraja klucza              | klucz zamaskowany
  T11 | pelny cykl kopia->szyfr->odtworzenie   | dane identyczne       (19.12)
  T12 | rotacja zachowuje N wersji             | N najnowszych kopii   (19.12)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.integrity as itg          # noqa: E402
import scripts.event_log as elog         # noqa: E402


# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def sample_dir(tmp_path):
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "a.txt").write_text("plik krytyczny A")
    (src / "sub" / "b.bin").write_bytes(bytes(range(256)) * 10)
    return src


@pytest.fixture
def key():
    return b"0123456789abcdef0123456789abcdef"


def _files(d: Path):
    return sorted(p for p in d.rglob("*") if p.is_file())


# --------------------------------------------------------------------------- testy

def test_T01_checksum_file(tmp_path):
    p = tmp_path / "x"
    p.write_bytes(b"abc")
    assert itg.checksum_file(p) == itg.checksum_bytes(b"abc")


def test_T02_manifest(sample_dir):
    m = itg.build_manifest(sample_dir, _files(sample_dir))
    assert {e.path for e in m.files} == {"a.txt", "sub/b.bin"}


def test_T03_signature_ok(sample_dir, key):
    m = itg.build_manifest(sample_dir, _files(sample_dir))
    itg.sign_manifest(m, key)
    assert itg.verify_signature(m, key)


def test_T04_tampered_manifest(sample_dir, key):
    m = itg.build_manifest(sample_dir, _files(sample_dir))
    itg.sign_manifest(m, key)
    m.files[0].checksum = "0" * 64
    with pytest.raises(itg.SignatureError):
        itg.verify_signature(m, key)


def test_T05_wrong_key(sample_dir, key):
    m = itg.build_manifest(sample_dir, _files(sample_dir))
    itg.sign_manifest(m, key)
    with pytest.raises(itg.SignatureError):
        itg.verify_signature(m, b"x" * 32)


def test_T06_missing_key(tmp_path):
    with pytest.raises(itg.MissingKeyError):
        itg.load_key(tmp_path / "brak.key")


def test_T07_corrupted_archive(sample_dir, key, tmp_path):
    archive = tmp_path / "backup.enc"
    archive.write_bytes(b"udawane zaszyfrowane dane" * 100)
    m = itg.build_manifest(sample_dir, _files(sample_dir))
    itg.attach_archive_checksum(m, archive)
    itg.sign_manifest(m, key)
    assert itg.verify_archive(m, archive, key)

    data = bytearray(archive.read_bytes())
    data[10] ^= 0xFF
    archive.write_bytes(bytes(data))
    with pytest.raises(itg.ChecksumMismatchError):
        itg.verify_archive(m, archive, key)


def test_T08_restored_files_match(sample_dir):
    m = itg.build_manifest(sample_dir, _files(sample_dir))
    assert itg.verify_restored_files(m, sample_dir) == []
    (sample_dir / "a.txt").write_text("zmienione")
    assert itg.verify_restored_files(m, sample_dir) == ["NIEZGODNA SUMA: a.txt"]


def test_T09_no_changes(sample_dir):
    m1 = itg.build_manifest(sample_dir, _files(sample_dir))
    m2 = itg.build_manifest(sample_dir, _files(sample_dir))
    assert itg.changed_files(m1, m2) == []


def test_T10_logs_mask_key(tmp_path):
    log = elog.setup_logger("t10", tmp_path / "logs", console=False)
    elog.log_event(log, elog.Event.KEY_MISSING, "key=SUPERTAJNYKLUCZ123")
    for h in log.handlers:
        h.flush()
    content = (tmp_path / "logs" / "t10.log").read_text()
    assert "SUPERTAJNYKLUCZ123" not in content
    assert "KEY_MISSING" in content


@pytest.mark.skip(reason="czeka na modul szyfrowania/odtwarzania (19.12)")
def test_T11_full_cycle():
    ...


@pytest.mark.skip(reason="czeka na modul rotacji (19.12)")
def test_T12_rotation():
    ...
