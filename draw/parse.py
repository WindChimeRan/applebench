"""Parse metalstat.jsonl sidecars produced by the weekly benchmark pipeline.

Each *_metalstat.jsonl line is one per-second sample with GPU/CPU/memory/power
metrics; filenames look like `<framework>_<YYYYMMDD>_<HHMMSS>_metalstat.jsonl`.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

FILENAME_RE = re.compile(
    r"^(?P<framework>.+)_(?P<date>\d{8})_(?P<time>\d{6})_metalstat\.jsonl$"
)


@dataclass
class Trace:
    framework: str
    timestamp: str
    path: Path
    rows: list[dict]

    @property
    def elapsed_s(self) -> list[float]:
        return [r["elapsed_s"] for r in self.rows]

    def series(self, key: str) -> list[float | None]:
        return [r.get(key) for r in self.rows]


def discover_traces(split_dir: Path) -> dict[str, Trace]:
    """One Trace per framework in `split_dir` — the latest timestamp wins."""
    by_fw: dict[str, Trace] = {}
    for path in sorted(split_dir.glob("*_metalstat.jsonl")):
        m = FILENAME_RE.match(path.name)
        if not m:
            continue
        fw = m["framework"]
        ts = f"{m['date']}_{m['time']}"
        if fw in by_fw and by_fw[fw].timestamp >= ts:
            continue
        rows = [
            json.loads(line)
            for line in path.read_text().splitlines()
            if line.strip()
        ]
        if not rows:
            continue
        by_fw[fw] = Trace(framework=fw, timestamp=ts, path=path, rows=rows)
    return by_fw
