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
    wall_times: dict[int, float]  # concurrency -> wall_time_s (0 if phase skipped/crashed)

    @property
    def elapsed_s(self) -> list[float]:
        return [r["elapsed_s"] for r in self.rows]

    def series(self, key: str) -> list[float | None]:
        return [r.get(key) for r in self.rows]

    def phase_slice(self, concurrency: int) -> tuple[list[float], list[int]] | None:
        """Rows belonging to the given concurrency level, by cumulative wall_times.

        Approximation: phases are laid out contiguously from the start of the
        trace in concurrency order, each taking its recorded wall_time_s.
        Warmup/gap time between phases is absorbed into the next phase head.
        Returns (x_percent_within_phase, row_indices), or None if that phase
        has wall_time_s ~0 (skipped/crashed with no useful window).
        """
        order = sorted(self.wall_times)
        offset = 0.0
        bounds = {}
        for c in order:
            w = self.wall_times[c]
            bounds[c] = (offset, offset + w)
            offset += w
        if concurrency not in bounds:
            return None
        start, end = bounds[concurrency]
        if end - start < 1.0:
            return None
        idxs = [
            i for i, e in enumerate(self.elapsed_s)
            if start <= e < end
        ]
        if not idxs:
            return None
        x_pct = [
            100.0 * (self.elapsed_s[i] - start) / (end - start) for i in idxs
        ]
        return x_pct, idxs


def _load_wall_times(result_json: Path) -> dict[int, float]:
    if not result_json.exists():
        return {}
    data = json.loads(result_json.read_text())
    out: dict[int, float] = {}
    for r in data.get("concurrency_results", []):
        c = r.get("concurrency")
        if c is None:
            continue
        out[int(c)] = float(r.get("wall_time_s") or 0)
    return out


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
        result_json = path.with_name(f"{fw}_{m['date']}_{m['time']}.json")
        wall_times = _load_wall_times(result_json)
        by_fw[fw] = Trace(
            framework=fw, timestamp=ts, path=path, rows=rows,
            wall_times=wall_times,
        )
    return by_fw
