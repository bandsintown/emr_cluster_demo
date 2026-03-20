#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from typing import List, Tuple


def sh(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    ap.add_argument("--repo", required=True, help="ECR repository name")
    # NEW: Added registry-id for cross-account support
    ap.add_argument("--registry-id", required=False, help="AWS Account ID for the ECR registry")
    ap.add_argument("--service", required=False, help="Service name suffix filter")
    ap.add_argument("--all-tags", action="store_true", help="Print all tags")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()
    args.registry_id = '004095192903'

    # Build the AWS CLI command dynamically
    cmd = [
        "aws", "ecr", "describe-images",
        "--region", args.region,
        "--repository-name", args.repo,
        "--query", "imageDetails[*].{pushedAt:imagePushedAt,tags:imageTags}",
        "--output", "json",
    ]

    # If a different account ID is provided, add it to the command
    if args.registry_id:
        cmd.extend(["--registry-id", args.registry_id])

    out = sh(cmd)

    items = json.loads(out)
    rows: List[Tuple[str, str]] = []
    args.all_tags = True
    for item in items:
        pushed = item.get("pushedAt") or ""
        tags = item.get("tags") or []
        if not isinstance(tags, list): continue

        for t in tags:
            # Logic fix: Only filter if not --all-tags and service is provided
            if not args.all_tags and args.service:
                if not t.endswith(f"_{args.service}"):
                    continue
            rows.append((pushed, t))

    rows.sort(key=lambda x: x[0], reverse=True)

    for _, tag in rows[: args.limit]:
        print(tag)


if __name__ == "__main__":
    main()