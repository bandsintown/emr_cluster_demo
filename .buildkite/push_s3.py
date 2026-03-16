#!/usr/bin/env python3
"""Push mapped files for a given service to the correct S3 bucket.

- The service is passed as --image-tag (Buildkite image tag / service name).
- The set of files/dirs to upload is taken from the JSON mapping file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import boto3  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    boto3 = None  # type: ignore


def _load_json_allowing_double_slash_comments(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    raw = "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("//")
    )
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Mapping JSON must be an object")
    return data


def _iter_files(root: Path, pattern: str) -> list[Path]:
    """Return all files under root matching pattern.

    - If pattern is a dir (endswith '/'), returns all files under it.
    - If pattern is a file, returns that file.
    """
    # Normalize mapping entries like "hdfs/FanSEO/" or ".../file.hql"
    rel = pattern.lstrip("/")
    is_dir = rel.endswith("/")
    target = (root / rel.rstrip("/")).resolve()

    if is_dir:
        if not target.exists():
            return []
        return [p for p in target.rglob("*") if p.is_file()]

    return [target] if target.is_file() else []


class GitHubS3Uploader:
    def __init__(self, env: str = "prod"):
        if boto3 is None:
            raise SystemExit(
                "Missing dependency: boto3. Install it (e.g., pip install boto3) in the runtime environment."
            )
        session = boto3.Session(profile_name="bit-prod")
        s3_resource = session.resource("s3")

        if env == "prod":
            bucket_name = "bit-emr-cluster"
        elif env == "dev":
            bucket_name = "bit-emr-cluster-dev"
        else:
            raise SystemExit(f"Unknown environment: {env}")

        print(f"\n--- Uploading files to s3://{bucket_name}")
        self.bucket = s3_resource.Bucket(bucket_name)  # type: ignore

    def upload(self, *, local_root: Path, files: list[Path], dry_run: bool = False) -> None:
        for f in files:
            if not f.is_file():
                continue

            key = f.relative_to(local_root).as_posix()
            print(f"  Uploading: {f} -> s3://{self.bucket.name}/{key}")
            if dry_run:
                continue

            self.bucket.upload_file(Filename=str(f), Key=key)


def _service_from_image_tag(image_tag: str) -> str:
    # Accept either a plain service name or a build tag like '<sha>_<service>'
    # Use rsplit so service names containing '_' still work.
    return image_tag.rsplit("_", 1)[-1]


def _resolve_mapping_root(local_root: Path, entries: list[str], prefix: str | None, service: str) -> Path:
    """Determine where mapping paths live.

    Priority:
    1) If /app/<service> exists (staged image layout), use that.
    2) If prefix is provided, use local_root/prefix.
    3) Otherwise use local_root.
    """
    staged = (Path("/app") / service).resolve()
    if staged.exists():
        return staged

    if prefix:
        return (local_root / prefix).resolve()

    return local_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Push mapped files for a service to S3")
    parser.add_argument(
        "--environment",
        "--env",
        choices=["prod", "dev"],
        default="prod",
        help="Target environment (prod or dev)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Local repo root used to resolve mapping entries (default: current dir)",
    )
    parser.add_argument("--image-tag", required=True, help="Service name (must exist in mapping JSON)")
    parser.add_argument(
        "--json-mapping",
        default="/app/s3_mapping.json",
        help="Path to JSON mapping file (service -> list of files/dirs)",
    )
    parser.add_argument(
        "--mapping-root-prefix",
        help="Subdirectory under the repo root where mapping entries are located",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be uploaded without uploading")

    args = parser.parse_args()

    local_root = Path(args.root).resolve()
    mapping_path = Path(args.json_mapping).resolve()

    if not mapping_path.exists():
        raise SystemExit(f"Mapping file not found: {mapping_path}")

    mapping = _load_json_allowing_double_slash_comments(mapping_path)

    service = _service_from_image_tag(args.image_tag)
    if service not in mapping:
        available = ", ".join(sorted(str(k) for k in mapping.keys()))
        raise SystemExit(f"Unknown service '{args.image_tag}'. Available: {available}")

    entries = mapping[service]
    if not isinstance(entries, list) or not all(isinstance(x, str) for x in entries):
        raise SystemExit(f"Invalid mapping for '{service}': expected list of strings")

    mapping_root = _resolve_mapping_root(local_root, entries, args.mapping_root_prefix, service)

    # Collect files to upload (dedupe, keep stable order)
    seen: set[Path] = set()
    files: list[Path] = []
    for entry in entries:
        for f in _iter_files(mapping_root, entry):
            # If we are using staged root (/app/<service>), mapping entries should be relative
            # to that root. Strip any leading directories like 'hdfs/' already present.
            if f not in seen:
                seen.add(f)
                files.append(f)

    print("=== S3 Upload Configuration ===")
    print(f"Environment: {args.environment.upper()}")
    print(f"Service: {service}")
    print(f"Mapping: {mapping_path}")
    print(f"Root: {local_root}")
    print(f"Files to upload: {len(files)}")
    print("================================\n")

    uploader = GitHubS3Uploader(env=args.environment)
    uploader.upload(local_root=mapping_root, files=files, dry_run=args.dry_run)


if __name__ == "__main__":
    main()