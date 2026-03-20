#!/usr/bin/env python3
import argparse, json, os, subprocess


def sh(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print(f"AWS ERROR: {p.stderr}")
        return None
    return p.stdout


def main():
    # Use these specific values to match your environment
    REGISTRY_ID = "004095192903"
    REPO_NAME = "emr_cluster"  # CHECK FOR TYPOS HERE (cluser vs cluster)
    REGION = "us-east-1"  # DOUBLE CHECK REGION

    cmd = [
        "aws", "ecr", "describe-images",
        "--region", REGION,
        "--registry-id", REGISTRY_ID,
        "--repository-name", REPO_NAME,
        "--query", "imageDetails[*].{pushedAt:imagePushedAt,tags:imageTags}",
        "--output", "json"
    ]

    print(f"--- Checking Account {REGISTRY_ID} in {REGION} for repo: {REPO_NAME} ---")

    raw_output = sh(cmd)
    if not raw_output: return

    items = json.loads(raw_output)
    print(f"Found {len(items)} total image objects in ECR.")

    rows = []
    for item in items:
        pushed = str(item.get("pushedAt") or "Unknown Date")
        tags = item.get("tags") or []

        if not tags:
            # This is a common reason for "nothing" appearing
            print(f"Skipping untagged image pushed at {pushed}")
            continue

        for t in tags:
            print(f"Matched Tag: {t} (Pushed: {pushed})")
            rows.append((pushed, t))

    # Sort and print
    rows.sort(key=lambda x: x[0], reverse=True)
    print("\n--- TOP 10 RECENT TAGS ---")
    for _, tag in rows[:10]:
        print(tag)


if __name__ == "__main__":
    main()