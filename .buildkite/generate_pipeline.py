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
                "prompt": "Select the name of the service to build.",
                "type": "input",
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
                "label": "🚀 Build & Push Docker Image for $$SERVICE_NAME",
                "key": "build_and_push",
                "depends_on": "get_service_name",
                "commands": [
                    """# 1. Retrieve required variables from Meta-data\nSERVICE_NAME=\"$$(buildkite-agent meta-data get \\\"SERVICE_NAME\\\")\"\nAWS_ACCOUNT_ID=\"004095192903\"\nAWS_REGION=\"us-east-1\"\n\n# 2. Define/Calculate dependent variables\nBUILD_TAG=\"${BUILDKITE_COMMIT}_$${SERVICE_NAME}\"\nECR_REGISTRY_URI=\"${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com\"\nREPOSITORY_NAME=\"emr_cluster\"\nIMAGE_URI=\"$${ECR_REGISTRY_URI}/$${REPOSITORY_NAME}\"\nDOCKERFILE_PATH=\"Dockerfile\"\nBASE_DIR=\".\"\n\necho \"Selected service: $${SERVICE_NAME}\"\necho \"Calculated Image URI: $${IMAGE_URI}:$${BUILD_TAG}\"\necho \"--- Building Image ---\"\ndocker build \\\n  --file \"$${DOCKERFILE_PATH}\" \\\n  --build-arg SERVICE_NAME=\"$${SERVICE_NAME}\" \\\n  --tag \"$${IMAGE_URI}:$${BUILD_TAG}\" \\\n  .\n\necho \"--- Pushing Image to ECR ---\"\ndocker push \"$${IMAGE_URI}:$${BUILD_TAG}\"\n\n# STORE FOR DOWNSTREAM STEPS\nbuildkite-agent meta-data set \"IMAGE_URI\" \"$${IMAGE_URI}\"\nbuildkite-agent meta-data set \"BUILD_TAG\" \"$${BUILD_TAG}\"\nbuildkite-agent meta-data set \"AWS_REGION\" \"$${AWS_REGION}\"\nbuildkite-agent meta-data set \"AWS_ACCOUNT_ID\" \"$${AWS_ACCOUNT_ID}\"\n"""
                ],
            },
            {
                "block": "❓ Trigger S3 Asset Push?",
                "prompt": "Do you want to extract and push the static assets to S3?",
                "key": "ask_s3_push",
                "depends_on": "build_and_push",
                "fields": [
                    {
                        "select": "S3_CHOICE",
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
                "label": "pipeline: Setup pipeline",
                "key": "setup_pipline",
                "depends_on": "ask_s3_push",
                "command": """if [ \"$$(buildkite-agent meta-data get \\\"deploy-type\\\")\" == \"yes\" ]; then\n  buildkite-agent pipeline upload .buildkite/s3-push.yml\nfi\n""",
            },
        ]
    }

    print("# GENERATED FILE - DO NOT EDIT")
    print(yaml.safe_dump(pipeline, sort_keys=False))


if __name__ == "__main__":
    main()

