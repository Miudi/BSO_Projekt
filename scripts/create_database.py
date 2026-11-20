#!/usr/bin/env python3
"""
create_database.py - zbiera wskazany folder w jeden plik "bazy", potrafi go rowniez rozpakowac.
Plik bazy to standardowy ZIP + drzewo hashy (Merkle) w pliku MERKLE_TREE.json.
Domyslny katalog baz danych jest okreslony przez zmienna DB_DIR.
Tylko biblioteka standardowa.

  python3 create_database.py pack   test_data                 -> tworzy: <DB_DIR>/database.zip
  python3 create_database.py pack   test_data moja_baza.zip   -> tworzy: <DB_DIR>/moja_baza.zip
  python3 create_database.py verify                          -> weryfikuje <DB_DIR>/database.zip
  python3 create_database.py verify moja_baza.zip            -> weryfikuje <DB_DIR>/moja_baza.zip
  python3 create_database.py verify moja_baza.zip <root_hash> -> j.w. + porownuje z zaufanym root hashem
  python3 create_database.py unpack                          -> rozpakowuje <DB_DIR>/database.zip do <DB_DIR>
  python3 create_database.py unpack moja_baza.zip             -> rozpakowuje <DB_DIR>/moja_baza.zip do <DB_DIR>
  python3 create_database.py unpack moja_baza.zip odzysk      -> rozpakowuje <DB_DIR>/moja_baza.zip do <DB_DIR>/odzysk
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

DB_DIR = "databases"
DEFAULT_DB = "database.zip"
MANIFEST = "MERKLE_TREE.json"
ALGO = "sha256"


class DatabaseManager:
    """Klasa zarządzająca tworzeniem, weryfikacją i rozpakowywaniem bazy archiwów z drzewem Merkle."""

    def __init__(self, db_dir=DB_DIR):
        self.db_dir = Path(db_dir)

    def _resolve_db_path(self, db_file=DEFAULT_DB):
        """Zwraca ścieżkę do pliku bazy względem DB_DIR, chyba że podano konkretną ścieżkę."""
        p = Path(db_file)
        if p.is_absolute() or len(p.parts) > 1:
            return p.resolve()
        return (self.db_dir / p).resolve()

    def _resolve_unpack_dest(self, dest=None):
        """Zwraca katalog docelowy rozpakowania - domyślnie DB_DIR."""
        if dest is None:
            return self.db_dir.resolve()
        d = Path(dest)
        if d.is_absolute() or len(d.parts) > 1:
            return d.resolve()
        return (self.db_dir / d).resolve()

    def _hash_stream(self, f, chunk=1024 * 1024):
        h = hashlib.sha256()
        while block := f.read(chunk):
            h.update(block)
        return h.hexdigest()

    def _hash_file(self, path):
        with open(path, "rb") as f:
            return self._hash_stream(f)

    def _build_tree(self, file_hashes, dirs):
        children = {}
        for p in [*file_hashes, *dirs]:
            children.setdefault(p.rpartition("/")[0], []).append(p)

        def node(p):
            name = p.rpartition("/")[2]
            if p in file_hashes:
                return {"name": name, "type": "file", "hash": file_hashes[p]}
            kids = [node(c) for c in sorted(children.get(p, []))]
            h = hashlib.sha256()
            for k in kids:
                h.update(f"{k['type']}\0{k['name']}\0{k['hash']}\n".encode("utf-8"))
            return {"name": name, "type": "dir", "hash": h.hexdigest(), "children": kids}

        tops = children.get("", [])
        if len(tops) != 1:
            raise ValueError("Baza powinna mieć dokładnie jeden folder najwyższego poziomu.")
        return node(tops[0])

    def _flatten(self, node, prefix=""):
        p = f"{prefix}/{node['name']}" if prefix else node["name"]
        out = {p: node["hash"]}
        for c in node.get("children", []):
            out.update(self._flatten(c, p))
        return out

    def _check_zip(self, zf, expected_root=None):
        stored = json.loads(zf.read(MANIFEST))
        files, dirs = {}, set()
        for info in zf.infolist():
            if info.filename == MANIFEST:
                continue
            if info.is_dir():
                dirs.add(info.filename.rstrip("/"))
            else:
                with zf.open(info) as f:
                    files[info.filename] = self._hash_stream(f)
        actual = self._build_tree(files, dirs)

        problems = []
        if actual["hash"] != stored["root_hash"]:
            old, new = self._flatten(stored["tree"]), self._flatten(actual)
            for p in sorted(old.keys() | new.keys()):
                if p not in new:
                    problems.append(f"brakuje:   {p}")
                elif p not in old:
                    problems.append(f"nadmiarowy: {p}")
                elif old[p] != new[p]:
                    problems.append(f"zmieniony: {p}")
        if expected_root and actual["hash"] != expected_root:
            problems.append(f"root hash {actual['hash']} != oczekiwany {expected_root}")
        return problems, actual["hash"]

    def pack(self, src, db_file=DEFAULT_DB):
        """Pakuje wskazany folder do pliku bazy w katalogu DB_DIR wraz z manifestem hashy."""
        base = Path(src).resolve()
        out_db = self._resolve_db_path(db_file)

        if not base.is_dir():
            raise NotADirectoryError(f"To nie jest folder: {src}")
        if out_db.exists():
            raise FileExistsError(f"{out_db} już istnieje - nie nadpisuję.")
        if base in out_db.parents:
            raise ValueError("Plik bazy nie może leżeć wewnątrz pakowanego folderu.")

        out_db.parent.mkdir(parents=True, exist_ok=True)

        file_hashes, dir_set = {}, set()
        with zipfile.ZipFile(out_db, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in [base, *sorted(base.rglob("*"))]:
                if path.is_symlink():
                    continue
                arc = path.relative_to(base.parent).as_posix()
                zf.write(path, arc)
                if path.is_dir():
                    dir_set.add(arc)
                else:
                    file_hashes[arc] = self._hash_file(path)

            tree = self._build_tree(file_hashes, dir_set)
            zf.writestr(MANIFEST, json.dumps(
                {"algorithm": ALGO, "root_hash": tree["hash"], "tree": tree},
                indent=2, ensure_ascii=False))

        print(f"[+] {out_db}: {len(file_hashes)} plikow, {len(dir_set)} folderow "
              f"({out_db.stat().st_size / 1024 / 1024:.2f} MB)")
        print(f"[+] Root hash ({ALGO}): {tree['hash']}")
        return out_db

    def verify(self, db_file=DEFAULT_DB, expected_root=None):
        """Sprawdza integralność bazy danych (domyślnie z DB_DIR) na podstawie drzewa hashy."""
        resolved_db = self._resolve_db_path(db_file)
        if not zipfile.is_zipfile(resolved_db):
            raise ValueError(f"To nie jest poprawny plik bazy: {resolved_db}")
        with zipfile.ZipFile(resolved_db) as zf:
            if MANIFEST not in zf.namelist():
                raise FileNotFoundError(f"Brak {MANIFEST} - baza nie ma drzewa hashy.")
            problems, root = self._check_zip(zf, expected_root)
        if problems:
            print("[!] Weryfikacja NIEUDANA:")
            for p in problems:
                print("    -", p)
            raise ValueError("Weryfikacja integralności nie powiodła się.")
        print(f"[+] Weryfikacja OK, root hash: {root}")
        return root

    def unpack(self, db_file=DEFAULT_DB, dest=None):
        """Weryfikuje i rozpakowuje bazę (domyślnie z DB_DIR do DB_DIR)."""
        resolved_db = self._resolve_db_path(db_file)
        dest_path = self._resolve_unpack_dest(dest)
        if not zipfile.is_zipfile(resolved_db):
            raise ValueError(f"To nie jest poprawny plik bazy: {resolved_db}")

        with zipfile.ZipFile(resolved_db) as zf:
            names = [n for n in zf.namelist() if n != MANIFEST]
            for name in names:
                target = (dest_path / name).resolve()
                if dest_path not in target.parents and target != dest_path:
                    raise ValueError(f"Niebezpieczna ścieżka w bazie (Zip-Slip): {name}")

            if MANIFEST in zf.namelist():
                problems, root = self._check_zip(zf)
                if problems:
                    print("[!] Weryfikacja hashy NIEUDANA - nie rozpakowuję:")
                    for p in problems:
                        print("    -", p)
                    raise ValueError("Weryfikacja hashy przed wypakowaniem nie powiodła się.")
                print(f"[+] Weryfikacja OK, root hash: {root}")
            else:
                print(f"[!] Uwaga: brak {MANIFEST} - rozpakowuję bez weryfikacji.")

            top = {Path(n).parts[0] for n in names}
            for t in top:
                if (dest_path / t).exists():
                    raise FileExistsError(f"{dest_path / t} już istnieje - nie nadpisuję.")
            dest_path.mkdir(parents=True, exist_ok=True)
            zf.extractall(dest_path, members=names)
        print(f"[+] Rozpakowano do: {dest_path}")
        return dest_path


# Interfejs CLI (gdy uruchamiasz skrypt bezpośrednio w terminalu)
if __name__ == "__main__":
    a = sys.argv[1:]
    db_manager = DatabaseManager()

    try:
        if not a:
            sys.exit(__doc__)

        cmd = a[0]
        if cmd == "pack" and len(a) in (2, 3):
            db_manager.pack(a[1], a[2] if len(a) == 3 else DEFAULT_DB)
        elif cmd == "unpack" and len(a) in (1, 2, 3):
            db_file = a[1] if len(a) >= 2 else DEFAULT_DB
            dest = a[2] if len(a) == 3 else None
            db_manager.unpack(db_file, dest)
        elif cmd == "verify" and len(a) in (1, 2, 3):
            db_file = a[1] if len(a) >= 2 else DEFAULT_DB
            expected_root = a[2] if len(a) == 3 else None
            db_manager.verify(db_file, expected_root)
        else:
            sys.exit(__doc__)
    except Exception as err:
        sys.exit(f"[!] Błąd: {err}")