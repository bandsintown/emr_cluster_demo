#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from typing import List, Tuple  # Added missing import


def sh(cmd: list[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        # Use strip() to ensure clean error messages
        raise SystemExit(p.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    ap.add_argument("--repo", required=True, help="ECR repository name")
    ap.add_argument("--service", required=False, help="Service name suffix filter")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    # Changed hardcoded 'emr_cluster' to args.repo
    out = sh([
        "aws", "ecr", "describe-images",
        "--region", args.region,
        "--repository-name", args.repo,
        "--query", "imageDetails[*].{pushedAt:imagePushedAt,tags:imageTags}",
        "--output", "json",
    ])

    items = json.loads(out)
    rows: List[Tuple[str, str]] = []

    for item in items:
        pushed = item.get("pushedAt") or ""
        tags = item.get("tags") or []

        if not isinstance(tags, list):
            continue

        for t in tags:
            if not isinstance(t, str):
                continue

            # Match the suffix logic
            if args.service and not t.endswith(f"_{args.service}"):
                continue

            rows.append((pushed, t))

    # Sort by timestamp (pushed) descending
    rows.sort(key=lambda x: x[0], reverse=True)

    # Print unique tags only (to handle cases where limit is applied)
    for _, tag in rows[:args.limit]:
        print(tag)


main()