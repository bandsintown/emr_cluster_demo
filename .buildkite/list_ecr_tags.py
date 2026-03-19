#!/usr/bin/env python3
"""List recent ECR image tags for a repo, optionally filtered by service suffix.

This is used by the rollback pipeline to present a human-friendly list of
available tags.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess


def sh(cmd: list[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    ap.add_argument("--repo", required=True, help="ECR repository name, e.g. emr_cluster")
    ap.add_argument("--service", required=False, default= "DailyArtistMetrics", help="Optional service name suffix filter")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    out = sh(
        [
            "aws",
            "ecr",
            "describe-images",
            "--region",
            args.region,
            "--repository-name",
            "emr_cluster",
            "--query",
            "imageDetails[*].{pushedAt:imagePushedAt,tags:imageTags}",
            "--output",
            "json",
        ]
    )

    items = json.loads(out)
    rows: list[tuple[str, str]] = []
    for item in items:
        pushed = item.get("pushedAt") or ""
        tags = item.get("tags") or []
        if not isinstance(tags, list):
            continue
        for t in tags:
            print(t)
            if not isinstance(t, str):
                continue
            if args.service and not t.endswith(f"_{args.service}"):
                continue
            rows.append((pushed, t))

    rows.sort(key=lambda x: x[0], reverse=True)
    for _, tag in rows[: args.limit]:
        print(tag)


if __name__ == "__main__":
    main()
