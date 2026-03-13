#!/usr/bin/env python3
"""Generate Buildkite pipeline with SERVICE_NAME dropdown from s3_mapping.json keys."""

from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: PyYAML. Install it in the Buildkite agent environment."
    ) from e


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / ".buildkite" / "config" / "s3_mapping.json"


def load_service_names() -> list[str]:
    # s3_mapping.json includes a // filepath comment; strip //-comment lines.
    raw = MAPPING_PATH.read_text(encoding="utf-8")
    raw = "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("//")
    )
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("s3_mapping.json must be a JSON object mapping service->paths")
    names = sorted(str(k) for k in data.keys())
    if not names:
        raise SystemExit("No services found in s3_mapping.json")
    return names


def option(name: str) -> dict:
    return {"label": name, "value": name}


def main() -> None:
    services = load_service_names()

    pipeline = {
        "steps": [
            {
                "label": "⚙️ Select Service to Build",
                "key": "get_service_name",
                "type": "input",
                "prompt": "Select the name of the service to build.",
                "fields": [
                    {
                        "select": "SERVICE_NAME",
                        "key": "SERVICE_NAME",
                        "required": True,
                        "options": [option(s) for s in services],
                    }
                ],
            },
            {
                "label": "🚀 Build & Push Docker Image",
                "key": "build_and_push",
                "depends_on": "get_service_name",
                "commands": [
                    """set -euo pipefail

# 1. Retrieve the selected value from Buildkite Meta-data
SERVICE_NAME=$(buildkite-agent meta-data get "SERVICE_NAME")

if [ -z "${SERVICE_NAME}" ]; then
  echo "Error: SERVICE_NAME is required but was not found in meta-data." >&2
  exit 1
fi

echo "--- Configuration ---"
echo "Selected service: ${SERVICE_NAME}"

AWS_ACCOUNT_ID="004095192903"
AWS_REGION="us-east-1"
REPOSITORY_NAME="emr_cluster"

# 2. Define/Calculate dependent variables
BUILD_TAG="${BUILDKITE_COMMIT}_${SERVICE_NAME}"
ECR_REGISTRY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_REGISTRY_URI}/${REPOSITORY_NAME}"

echo "Calculated Image URI: ${IMAGE_URI}:${BUILD_TAG}"

echo "--- Building Image ---"
docker build \
  --file "Dockerfile" \
  --build-arg SERVICE_NAME="${SERVICE_NAME}" \
  --tag "${IMAGE_URI}:${BUILD_TAG}" \
  .

echo "--- Pushing Image to ECR ---"
docker push "${IMAGE_URI}:${BUILD_TAG}"

# 3. Store for downstream steps
buildkite-agent meta-data set "IMAGE_URI" "${IMAGE_URI}"
buildkite-agent meta-data set "BUILD_TAG" "${BUILD_TAG}"
buildkite-agent meta-data set "AWS_REGION" "${AWS_REGION}"
buildkite-agent meta-data set "AWS_ACCOUNT_ID" "${AWS_ACCOUNT_ID}"
"""
                ],
            },
            {
                "block": "❓ Trigger S3 Asset Push?",
                "key": "ask_s3_push",
                "depends_on": "build_and_push",
                "prompt": "Do you want to extract and push the static assets to S3?",
                "fields": [
                    {
                        "select": "Choice",
                        "key": "deploy-type",
                        "default": "yes",
                        "required": True,
                        "options": [
                            {"label": "Yes, push to S3", "value": "yes"},
                            {"label": "No, skip S3 push", "value": "no"},
                        ],
                    }
                ],
            },
            {
                "label": "🏗️ Setup S3 Pipeline",
                "key": "setup_pipeline",
                "depends_on": "ask_s3_push",
                "command": (
                    "if [ \"$(buildkite-agent meta-data get 'deploy-type')\" = \"yes\" ]; then\n"
                    "  buildkite-agent pipeline upload .buildkite/s3-push.yml\n"
                    "fi"
                ),
            },
        ]
    }

    print("# GENERATED FILE - DO NOT EDIT")
    print(yaml.safe_dump(pipeline, sort_keys=False))


if __name__ == "__main__":
    main()