#!/usr/bin/env python3
"""Stage service assets into /app/<service>/... using s3_mapping.json.

Expects to run inside the Docker build with the repo copied to /src.
Copies only mapped files/dirs for SERVICE_NAME while preserving their
relative paths.

Notes:
- s3_mapping.json paths are treated as relative to MAPPING_ROOT (default: /src).
- Comment lines starting with '//' are ignored.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


def load_mapping(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    raw = "\n".join(line for line in raw.splitlines() if not line.lstrip().startswith("//"))
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("s3_mapping.json must be a JSON object")
    return data


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    service = os.environ.get("SERVICE_NAME")
    if not service:
        raise SystemExit("SERVICE_NAME is required")

    mapping_path = Path(os.environ.get("S3_MAPPING_PATH", "/src/.buildkite/config/s3_mapping.json"))
    mapping_root = Path(os.environ.get("MAPPING_ROOT", "/src")).resolve()
    out_root = Path(os.environ.get("OUT_ROOT", "/app")).resolve() / service

    mapping = load_mapping(mapping_path)
    paths = mapping.get(service)
    if not isinstance(paths, list) or not all(isinstance(x, str) for x in paths):
        raise SystemExit(f"No mapping found for service: {service}")

    out_root.mkdir(parents=True, exist_ok=True)

    for entry in paths:
        rel = entry.lstrip("/")
        if rel.endswith("/"):
            base = (mapping_root / rel.rstrip("/")).resolve()
            if not base.exists():
                continue
            for f in base.rglob("*"):
                if f.is_file():
                    dest = out_root / f.relative_to(mapping_root)
                    copy_file(f, dest)
        else:
            f = (mapping_root / rel).resolve()
            if f.is_file():
                dest = out_root / f.relative_to(mapping_root)
                copy_file(f, dest)


if __name__ == "__main__":
    main()

