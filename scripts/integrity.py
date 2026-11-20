"""
integrity.py - sumy kontrolne i podpisywanie kopii zapasowych.

Mechanizm:
  * SHA-256 dla kazdego pliku zrodlowego i dla calego archiwum kopii,
  * manifest JSON z lista plikow, rozmiarami i skrotami,
  * podpis HMAC-SHA256 manifestu (klucz tajny przechowywany poza kopia).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

HASH_ALGORITHM = "sha256"
CHUNK_SIZE = 64 * 1024          # czytanie plikow w blokach 64 KiB
MANIFEST_VERSION = 1


class IntegrityError(Exception):
    """Bazowy wyjatek bledow integralnosci."""


class ChecksumMismatchError(IntegrityError):
    """Suma kontrolna nie zgadza sie z zapisana w manifescie."""


class SignatureError(IntegrityError):
    """Podpis manifestu jest niepoprawny lub go brakuje."""


class MissingKeyError(IntegrityError):
    """Brak klucza potrzebnego do podpisu / weryfikacji."""


# ---------------------------------------------------------------------------
# Sumy kontrolne
# ---------------------------------------------------------------------------

def checksum_bytes(data: bytes) -> str:
    """Zwraca skrot SHA-256 (hex) dla danych w pamieci."""
    return hashlib.new(HASH_ALGORITHM, data).hexdigest()


def checksum_file(path: str | Path) -> str:
    """Zwraca skrot SHA-256 (hex) pliku, czytajac go blokami."""
    h = hashlib.new(HASH_ALGORITHM)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

@dataclass
class FileEntry:
    path: str            # sciezka wzgledna wzgledem katalogu zrodlowego
    size: int
    mtime: float
    checksum: str


@dataclass
class Manifest:
    backup_id: str
    created_at: str
    source_dir: str
    algorithm: str = HASH_ALGORITHM
    version: int = MANIFEST_VERSION
    files: list[FileEntry] = field(default_factory=list)
    archive_checksum: str | None = None   # skrot zaszyfrowanego archiwum
    signature: str | None = None          # HMAC calego manifestu

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Manifest":
        files = [FileEntry(**e) for e in d.get("files", [])]
        return cls(**{**d, "files": files})


def build_manifest(source_dir: str | Path, files: list[str | Path],
                   backup_id: str | None = None) -> Manifest:
    """Tworzy manifest z sumami kontrolnymi plikow przeznaczonych do kopii."""
    source_dir = Path(source_dir).resolve()
    now = datetime.now(timezone.utc)
    manifest = Manifest(
        backup_id=backup_id or now.strftime("backup_%Y%m%d_%H%M%S"),
        created_at=now.isoformat(),
        source_dir=str(source_dir),
    )
    for p in files:
        p = Path(p).resolve()
        st = p.stat()
        manifest.files.append(FileEntry(
            path=str(p.relative_to(source_dir)),
            size=st.st_size,
            mtime=st.st_mtime,
            checksum=checksum_file(p),
        ))
    return manifest


def save_manifest(manifest: Manifest, path: str | Path) -> None:
    """Zapisuje manifest do pliku JSON (uprawnienia 0600)."""
    path = Path(path)
    path.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
                    encoding="utf-8")
    os.chmod(path, 0o600)


def load_manifest(path: str | Path) -> Manifest:
    """Wczytuje manifest z pliku JSON."""
    return Manifest.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Podpisywanie (HMAC-SHA256)
# ---------------------------------------------------------------------------

def load_key(key_path: str | Path) -> bytes:
    """Wczytuje klucz podpisu z pliku. Rzuca MissingKeyError, gdy go brak."""
    key_path = Path(key_path)
    if not key_path.is_file():
        raise MissingKeyError(f"Brak pliku klucza: {key_path}")
    key = key_path.read_bytes().strip()
    if len(key) < 32:
        raise MissingKeyError("Klucz jest za krotki (wymagane min. 32 bajty)")
    return key


def generate_key(key_path: str | Path) -> None:
    """Generuje losowy klucz 32 B (hex) i zapisuje go z uprawnieniami 0600."""
    key_path = Path(key_path)
    key_path.write_text(os.urandom(32).hex(), encoding="ascii")
    os.chmod(key_path, 0o600)


def _canonical_bytes(manifest: Manifest) -> bytes:
    """Kanoniczna postac manifestu do podpisu (bez pola signature)."""
    d = manifest.to_dict()
    d.pop("signature", None)
    return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_manifest(manifest: Manifest, key: bytes) -> str:
    """Podpisuje manifest HMAC-SHA256 i zapisuje podpis w manifest.signature."""
    if not key:
        raise MissingKeyError("Nie podano klucza do podpisu")
    manifest.signature = hmac.new(key, _canonical_bytes(manifest),
                                  hashlib.sha256).hexdigest()
    return manifest.signature


def verify_signature(manifest: Manifest, key: bytes) -> bool:
    """Sprawdza podpis manifestu. Rzuca SignatureError przy niezgodnosci."""
    if not manifest.signature:
        raise SignatureError("Manifest nie jest podpisany")
    expected = hmac.new(key, _canonical_bytes(manifest), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, manifest.signature):
        raise SignatureError("Niepoprawny podpis manifestu (manifest zmieniony lub zly klucz)")
    return True


# ---------------------------------------------------------------------------
# Weryfikacja kopii przed odtworzeniem
# ---------------------------------------------------------------------------

def attach_archive_checksum(manifest: Manifest, archive_path: str | Path) -> str:
    """Liczy skrot zaszyfrowanego archiwum i zapisuje go w manifescie.
    Wywolywac PRZED sign_manifest()."""
    manifest.archive_checksum = checksum_file(archive_path)
    return manifest.archive_checksum


def verify_archive(manifest: Manifest, archive_path: str | Path, key: bytes) -> bool:
    """Pelna weryfikacja kopii przed odtworzeniem:
    1) podpis manifestu, 2) suma kontrolna archiwum."""
    verify_signature(manifest, key)
    if not Path(archive_path).is_file():
        raise IntegrityError(f"Brak pliku archiwum: {archive_path}")
    actual = checksum_file(archive_path)
    if actual != manifest.archive_checksum:
        raise ChecksumMismatchError(
            f"Archiwum uszkodzone: oczekiwano {manifest.archive_checksum}, jest {actual}")
    return True


def verify_restored_files(manifest: Manifest, restored_dir: str | Path) -> list[str]:
    """Porownuje sumy plikow odtworzonych z manifestem.
    Zwraca liste problemow (pusta = wszystko zgodne)."""
    restored_dir = Path(restored_dir)
    problems: list[str] = []
    for e in manifest.files:
        p = restored_dir / e.path
        if not p.is_file():
            problems.append(f"BRAK: {e.path}")
        elif checksum_file(p) != e.checksum:
            problems.append(f"NIEZGODNA SUMA: {e.path}")
    return problems


def changed_files(old: Manifest, new: Manifest) -> list[str]:
    """Zwraca pliki zmienione/dodane miedzy dwoma manifestami
    (przydatne do wykrywania braku zmian miedzy kopiami)."""
    old_map = {e.path: e.checksum for e in old.files}
    return [e.path for e in new.files if old_map.get(e.path) != e.checksum]
