#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
files_generator.py - Moduł generujący zestaw realistycznych plików testowych.
Może być używany jako samodzielny skrypt lub importowany jako moduł w Pythonie.
"""

import configparser
import io
import json
import random
import string
import uuid
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


class TestDataGenerator:
    """Klasa generująca kontrolowany zestaw plików testowych (config, logi, skrypty, notatki)."""

    def __init__(
        self,
        num_files=500,
        max_total_mb=200,
        safety_margin_mb=5,
        output_dir="test_data",
        random_seed=None
    ):
        self.num_files = num_files
        self.max_total_mb = max_total_mb
        self.safety_margin_mb = safety_margin_mb
        self.output_dir = Path(output_dir)
        self.random_seed = random_seed

        self.mb = 1024 * 1024
        self.max_bytes = (self.max_total_mb - self.safety_margin_mb) * self.mb

        self.log_min_bytes = 250 * 1024
        self.log_max_bytes = 1024 * 1024
        self.min_other_file_bytes = 2 * 1024

        self.file_types = {
            "json": ("config", 18),
            "yaml": ("config", 16),
            "ini":  ("config", 10),
            "conf": ("config", 10),
            "log":  ("logs",   22),
            "txt":  ("docs",   10),
            "py":   ("scripts", 14),
        }

        self.words = (
            "system kernel service daemon session token cache queue worker "
            "database backup network gateway cluster policy audit certificate "
            "storage volume mount update restore request response timeout "
            "retry handler module plugin scheduler metric alert"
        ).split()
        self.services = [
            "nginx", "postgres", "redis", "sshd", "cron", "auth-api",
            "payment-svc", "backup-agent", "kubelet", "systemd"
        ]
        self.levels = ["DEBUG", "INFO", "INFO", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def _rnd_str(self, n=12):
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    def _rnd_key(self):
        return "_".join(random.choices(self.words, k=random.randint(1, 3)))

    def _rnd_ip(self):
        return ".".join(str(random.randint(1, 254)) for _ in range(4))

    def _rnd_sentence(self, n=None):
        n = n or random.randint(5, 14)
        s = " ".join(random.choices(self.words, k=n))
        return s.capitalize() + "."

    def _rnd_value(self):
        kind = random.choice(["int", "float", "bool", "str", "ip", "path"])
        if kind == "int":
            return random.randint(1, 65535)
        if kind == "float":
            return round(random.uniform(0, 100), 3)
        if kind == "bool":
            return random.choice([True, False])
        if kind == "ip":
            return self._rnd_ip()
        if kind == "path":
            return "/var/lib/" + "/".join(random.choices(self.words, k=2))
        return self._rnd_str(random.randint(6, 24))

    def _gen_json(self):
        def section(depth=0):
            d = {}
            for _ in range(random.randint(3, 8)):
                if depth < 2 and random.random() < 0.3:
                    d[self._rnd_key()] = section(depth + 1)
                elif random.random() < 0.2:
                    d[self._rnd_key()] = [self._rnd_value() for _ in range(random.randint(2, 6))]
                else:
                    d[self._rnd_key()] = self._rnd_value()
            return d

        data = {
            "service": random.choice(self.services),
            "version": f"{random.randint(1, 9)}.{random.randint(0, 20)}.{random.randint(0, 99)}",
            "instance_id": str(uuid.uuid4()),
            "api_key": self._rnd_str(40),
            "settings": section(),
            "endpoints": [f"http://{self._rnd_ip()}:{random.randint(1024, 65535)}/api"
                          for _ in range(random.randint(1, 4))],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _gen_yaml(self):
        service = random.choice(self.services)
        lines = [f"# Konfiguracja {service} - wygenerowana automatycznie",
                 f"name: {service}",
                 f"replicas: {random.randint(1, 8)}",
                 f"secret: {self._rnd_str(32)}",
                 "settings:"]
        for _ in range(random.randint(4, 10)):
            v = self._rnd_value()
            v = str(v).lower() if isinstance(v, bool) else v
            lines.append(f"  {self._rnd_key()}: {v}")
        lines.append("hosts:")
        for _ in range(random.randint(2, 5)):
            lines.append(f"  - {self._rnd_ip()}")
        lines.append("limits:")
        lines.append(f"  cpu: {random.randint(1, 16)}")
        lines.append(f"  memory: {random.choice([256, 512, 1024, 2048])}Mi")
        return "\n".join(lines) + "\n"

    def _gen_ini(self):
        cp = configparser.ConfigParser()
        for _ in range(random.randint(2, 5)):
            sec = self._rnd_key()
            cp[sec] = {self._rnd_key(): str(self._rnd_value()) for _ in range(random.randint(3, 8))}
        cp["credentials"] = {"user": self._rnd_str(8), "password": self._rnd_str(20)}
        buf = io.StringIO()
        buf.write("; Plik INI wygenerowany automatycznie\n")
        cp.write(buf)
        return buf.getvalue()

    def _gen_conf(self):
        service = random.choice(self.services)
        lines = [f"# {service}.conf - plik konfiguracyjny",
                 f"# Ostatnia zmiana: {datetime.now():%Y-%m-%d %H:%M}"]
        for _ in range(random.randint(8, 25)):
            lines.append(f"{self._rnd_key()} = {self._rnd_value()}")
        lines.append(f"\nlisten {self._rnd_ip()}:{random.randint(1024, 65535)};")
        lines.append(f"include /etc/{service}/conf.d/*.conf;")
        return "\n".join(lines) + "\n"

    def _gen_txt(self):
        paragraphs = []
        for i in range(random.randint(3, 15)):
            paragraphs.append(" ".join(self._rnd_sentence() for _ in range(random.randint(2, 6))))
        header = f"NOTATKI ADMINISTRATORA #{random.randint(1, 999)}\n" + "=" * 40 + "\n\n"
        return header + "\n\n".join(paragraphs) + "\n"

    def _gen_py(self):
        fn = self._rnd_key()
        cls = "".join(w.capitalize() for w in random.choices(self.words, k=2))
        service = random.choice(self.services)
        return f'''#!/usr/bin/env python3
"""Skrypt pomocniczy: {self._rnd_sentence(6)}"""
import logging
import os

LOG = logging.getLogger("{service}")
TOKEN = "{self._rnd_str(32)}"
TIMEOUT = {random.randint(5, 120)}


class {cls}:
    def __init__(self, host="{self._rnd_ip()}", port={random.randint(1024, 65535)}):
        self.host = host
        self.port = port

    def {fn}(self, retries={random.randint(1, 5)}):
        for attempt in range(retries):
            LOG.info("proba %d / %d -> %s:%d", attempt + 1, retries, self.host, self.port)
        return os.getpid()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print({cls}().{fn}())
'''

    def _make_log_line(self, ts):
        return (f"{ts:%Y-%m-%d %H:%M:%S} [{random.choice(self.levels):8}] "
                f"{random.choice(self.services)}[{random.randint(100, 99999)}]: "
                f"{self._rnd_sentence()} client={self._rnd_ip()} req_id={self._rnd_str(10)} "
                f"took={random.randint(1, 5000)}ms")

    def _gen_log(self, target_bytes):
        ts = datetime.now() - timedelta(days=random.randint(1, 30))
        out, size = [], 0
        while True:
            ts += timedelta(seconds=random.randint(0, 30))
            line = self._make_log_line(ts) + "\n"
            n = len(line.encode("utf-8"))
            if size + n > target_bytes:
                break
            out.append(line)
            size += n
        return "".join(out)

    def generate(self):
        """Uruchamia proces generowania plików testowych."""
        if self.random_seed is not None:
            random.seed(self.random_seed)

        if self.output_dir.exists():
            import shutil
            shutil.rmtree(self.output_dir)

        if self.num_files * self.min_other_file_bytes > self.max_bytes:
            raise ValueError("NUM_FILES jest zbyt duze, aby zmiescic sie w limicie rozmiaru.")

        for sub in {sub for sub, _ in self.file_types.values()}:
            (self.output_dir / sub).mkdir(parents=True, exist_ok=True)

        types = list(self.file_types)
        weights = [self.file_types[t][1] for t in types]

        counts = Counter()
        total_bytes = 0

        for i in range(self.num_files):
            ftype = random.choices(types, weights=weights)[0]
            subdir = self.file_types[ftype][0]
            name = f"{random.choice(self.services)}_{i:04d}_{self._rnd_str(4)}.{ftype}"
            path = self.output_dir / subdir / name

            if ftype == "log":
                remaining = self.num_files - i - 1
                budget = self.max_bytes - total_bytes - remaining * self.min_other_file_bytes
                target = random.randint(self.log_min_bytes, self.log_max_bytes)
                target = max(1024, min(target, budget))
                content = self._gen_log(target)
            else:
                content = {
                    "json": self._gen_json,
                    "yaml": self._gen_yaml,
                    "ini": self._gen_ini,
                    "conf": self._gen_conf,
                    "txt": self._gen_txt,
                    "py": self._gen_py
                }[ftype]()

            path.write_text(content, encoding="utf-8")
            total_bytes += path.stat().st_size
            counts[ftype] += 1

        real_total = sum(p.stat().st_size for p in self.output_dir.rglob("*") if p.is_file())
        real_files = sum(1 for p in self.output_dir.rglob("*") if p.is_file())
        total_mb = real_total / self.mb

        print("=" * 50)
        print("PODSUMOWANIE")
        print("=" * 50)
        print(f"Katalog wyjsciowy : {self.output_dir.resolve()}")
        print(f"Utworzone pliki   : {real_files} (zadano: {self.num_files})")
        print("Rozklad typow     :")
        for t, c in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  .{t:<5} {c:>4}  ({self.file_types[t][0]}/)")
        print(f"Laczny rozmiar    : {total_mb:.2f} MB")
        ok = total_mb <= self.max_total_mb
        print(f"Limit {self.max_total_mb} MB      : {'OK - miesci sie w limicie' if ok else 'PRZEKROCZONY!'}")
        
        return self.output_dir


# Interfejs CLI (gdy uruchamiasz skrypt bezpośrednio w terminalu)
if __name__ == "__main__":
    generator = TestDataGenerator(
        num_files=500,
        max_total_mb=200,
        safety_margin_mb=5,
        output_dir="test_data",
        random_seed=None
    )
    try:
        generator.generate()
    except Exception as err:
        sys.exit(f"[!] Błąd: {err}")