#!/usr/bin/env python3
"""
file_crypto.py - Moduł do szyfrowania i deszyfrowania plików (Fernet: AES + HMAC).
Domyślny katalog plików baz danych jest określony przez zmienną DB_DIR,
a katalog klucza przez KEY_DIR (domyślnie równy DB_DIR).
Może być używany jako samodzielny skrypt lub importowany jako moduł w Pythonie.
  python3 file_crypto.py encrypt database.zip      -> szyfruje <DB_DIR>/database.zip -> <DB_DIR>/database.zip.enc (klucz w <KEY_DIR>/file.key)
  python3 file_crypto.py decrypt database.zip.enc  -> odszyfrowuje <DB_DIR>/database.zip.enc -> <DB_DIR>/database.zip
"""
import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

DB_DIR = "databases"
KEY_DIR = DB_DIR
DEFAULT_KEY = "file.key"


class FileCrypto:
    def __init__(self, key_path=DEFAULT_KEY, db_dir=DB_DIR, key_dir=KEY_DIR):
        self.db_dir = Path(db_dir)
        self.key_dir = Path(key_dir)
        self.key_path = self._resolve_key_path(key_path)

    def _resolve_key_path(self, key_path):
        """Zwraca ścieżkę do pliku klucza względem key_dir, chyba że podano konkretną ścieżkę."""
        p = Path(key_path)
        if p.is_absolute() or len(p.parts) > 1:
            return p.resolve()
        return (self.key_dir / p).resolve()

    def _resolve_input_path(self, file_path):
        """Zwraca ścieżkę do pliku względem DB_DIR (jeśli podano samą nazwę), z fallbackiem na bieżący katalog."""
        p = Path(file_path)
        if p.is_absolute() or len(p.parts) > 1:
            return p.resolve()

        in_db_dir = (self.db_dir / p).resolve()
        if in_db_dir.exists():
            return in_db_dir

        in_cwd = p.resolve()
        if in_cwd.exists():
            return in_cwd

        return in_db_dir

    def _resolve_output_path(self, src, dst_path=None, default_dst=None):
        """Zwraca ścieżkę wyjściową; gdy nie podano dst_path, zapisuje w katalogu pliku źródłowego."""
        if dst_path:
            d = Path(dst_path)
            if d.is_absolute() or len(d.parts) > 1:
                return d.resolve()
            return (src.parent / d).resolve()
        return default_dst.resolve()

    def _get_key(self, create=False):
        """Wczytuje klucz; przy szyfrowaniu tworzy nowy, jeśli go nie ma (prawa 600)."""
        if not self.key_path.exists():
            if not create:
                raise FileNotFoundError(f"Brak pliku klucza: {self.key_path}")
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(Fernet.generate_key())
            print(f"[+] Nowy klucz: {self.key_path}")
        return self.key_path.read_bytes()

    def encrypt_file(self, src_path, dst_path=None):
        """Szyfruje wskazany plik."""
        src = self._resolve_input_path(src_path)
        default_dst = src.with_name(src.name + ".enc")
        dst = self._resolve_output_path(src, dst_path, default_dst)

        if not src.is_file():
            raise FileNotFoundError(f"Nie znaleziono pliku do zaszyfrowania: {src}")
        if dst.exists():
            raise FileExistsError(f"Plik docelowy {dst} już istnieje.")

        fernet = Fernet(self._get_key(create=True))
        try:
            data = src.read_bytes()
            encrypted_data = fernet.encrypt(data)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(encrypted_data)
        except Exception as e:
            raise RuntimeError(f"Błąd podczas szyfrowania pliku {src}: {e}")

        print(f"[+] Zaszyfrowano: {src} -> {dst}")
        return dst

    def decrypt_file(self, src_path, dst_path=None):
        """Odszyfrowuje wskazany plik."""
        src = self._resolve_input_path(src_path)
        default_dst = src.with_suffix("") if src.suffix == ".enc" else src.with_name(src.name + ".dec")
        dst = self._resolve_output_path(src, dst_path, default_dst)

        if not src.is_file():
            raise FileNotFoundError(f"Nie znaleziono pliku do odszyfrowania: {src}")
        if dst.exists():
            raise FileExistsError(f"Plik docelowy {dst} już istnieje.")

        fernet = Fernet(self._get_key(create=False))
        try:
            data = src.read_bytes()
            decrypted_data = fernet.decrypt(data)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(decrypted_data)
        except InvalidToken:
            raise ValueError("Zły klucz lub uszkodzony plik (InvalidToken).")
        except Exception as e:
            raise RuntimeError(f"Błąd deszyfrowania: {e}")

        print(f"[+] Odszyfrowano: {src} -> {dst}")
        return dst


# Interfejs CLI (gdy uruchamiasz plik bezpośrednio w terminalu)
if __name__ == "__main__":
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in ("encrypt", "decrypt"):
        sys.exit("Użycie: python3 file_crypto.py encrypt|decrypt <plik> [plik_docelowy]")

    mode, target = sys.argv[1], sys.argv[2]
    dst = sys.argv[3] if len(sys.argv) == 4 else None
    crypto = FileCrypto()

    try:
        if mode == "encrypt":
            crypto.encrypt_file(target, dst)
        else:
            crypto.decrypt_file(target, dst)
    except Exception as err:
        sys.exit(f"[!] Błąd: {err}")