#!/usr/bin/env python3
"""Generate Buildkite pipeline with SERVICE_NAME dropdown from s3_mapping.json keys."""

from __future__ import annotations
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("Missing dependency: PyYAML. Install it with 'pip install pyyaml'.")

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / ".buildkite" / "config" / "s3_mapping.json"

def load_service_names() -> list[str]:
    raw = MAPPING_PATH.read_text(encoding="utf-8")
    raw = "\n".join(line for line in raw.splitlines() if not line.lstrip().startswith("//"))
    data = json.loads(raw)
    names = sorted(str(k) for k in data.keys())
    if not names:
        raise SystemExit("No services found in s3_mapping.json")
    return names

def main() -> None:
    services = load_service_names()

    pipeline = {
        "steps": [
            # {
            #     "label": "⚙️ Select Service to Build",
            #     "key": "get_service_name",
            #     "type": "input",
            #     "fields": [
            #         {
            #             "select": "SERVICE_NAME",
            #             "key": "SERVICE_NAME",
            #             "required": True,
            #             "options": [{"label": s, "value": s} for s in services],
            #         }
            #     ],
            # },
            # {
            #     "label": "🚀 Build & Push Docker Image",
            #     "key": "build_and_push",
            #     "depends_on": "get_service_name",
            #     "commands": [
            #     "set -euo pipefail\n"
            #     "AWS_ACCOUNT_ID='004095192903'\n"
            #     "AWS_REGION='us-east-1'\n"
            #     "\n"
            #     "# 1. Authenticate Docker to ECR\n"
            #     "echo '--- Authenticating with ECR ---'\n"
            #     "aws ecr get-login-password --region $${AWS_REGION} | docker login --username AWS --password-stdin $${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com\n"
            #     "\n"
            #     "# 2. Retrieve SERVICE_NAME from meta-data\n"
            #     "SERVICE_NAME=$$(buildkite-agent meta-data get 'SERVICE_NAME')\n"
            #     "if [ -z \"$${SERVICE_NAME}\" ]; then\n"
            #     "  echo 'Error: SERVICE_NAME is required' >&2\n"
            #     "  exit 1\n"
            #     "fi\n"
            #     "\n"
            #     "REPOSITORY_NAME='emr_cluster'\n"
            #     "BUILD_TAG=\"$${BUILDKITE_COMMIT}_$${SERVICE_NAME}\"\n"
            #     "ECR_URI=\"$${AWS_ACCOUNT_ID}.dkr.ecr.$${AWS_REGION}.amazonaws.com\"\n"
            #     "IMAGE_URI=\"$${ECR_URI}/$${REPOSITORY_NAME}\"\n"
            #     "\n"
            #     "echo \"--- Building $${SERVICE_NAME} ---\"\n"
            #     "docker build --build-arg SERVICE_NAME=\"$${SERVICE_NAME}\" -t \"$${IMAGE_URI}:$${BUILD_TAG}\" .\n"
            #     "\n"
            #     "echo '--- Pushing to ECR ---'\n"
            #     "docker push \"$${IMAGE_URI}:$${BUILD_TAG}\"\n"
            #     "\n"
            #     "buildkite-agent meta-data set 'IMAGE_URI' \"$${IMAGE_URI}\"\n"
            #     "buildkite-agent meta-data set 'BUILD_TAG' \"$${BUILD_TAG}\""
            # ],
            # },
            # {
            #     "block": "❓ Trigger S3 Asset Push?",
            #     "key": "ask_s3_push",
            #     "depends_on": "build_and_push",
            #     "fields": [
            #         {
            #             "select": "Choice",
            #             "key": "deploy-type",
            #             "default": "yes",
            #             "options": [
            #                 {"label": "Yes", "value": "yes"},
            #                 {"label": "No", "value": "no"},
            #             ],
            #         }
            #     ],
            # },
            # {
            #     "label": "🏗️ Setup S3 Pipeline",
            #     "key": "setup_pipeline",
            #     "depends_on": "ask_s3_push",
            #     "command": (
            #         "if [ \"$$(buildkite-agent meta-data get 'deploy-type')\" = 'yes' ]; then\n"
            #         "  buildkite-agent pipeline upload .buildkite/s3-push.yml\n"
            #         "fi"
            #     ),
            # },
            {
                "block": "⏪ Roll back to a previous image?",
                "key": "ask_rollback",
                # "depends_on": "setup_pipeline",
                "fields": [
                    {
                        "select": "Rollback",
                        "key": "do-rollback",
                        "default": "no",
                        "required": True,
                        "options": [
                            {"label": "No", "value": "no"},
                            {"label": "Yes", "value": "yes"},
                        ],
                    }
                ],
            },
            {
                "label": "⏪ Setup rollback pipeline",
                "key": "setup_rollback",
                "depends_on": "ask_rollback",
                "command": (
                    "if [ \"$$(buildkite-agent meta-data get 'do-rollback')\" = 'yes' ]; then\n"
                    "  buildkite-agent pipeline upload .buildkite/roll_back.yml\n"
                    "fi"
                ),
            },
        ]
    }

    print("# GENERATED FILE - DO NOT EDIT")
    print(yaml.safe_dump(pipeline, sort_keys=False))

if __name__ == "__main__":
    main()