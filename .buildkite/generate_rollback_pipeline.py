#!/usr/bin/env python3
"""Generate the rollback pipeline with a service dropdown from s3_mapping.json keys.

Buildkite pipeline YAML is static, so we generate it at runtime (same approach
as generate_pipeline.py).

This generator produces a rollback pipeline that:
1) asks user to select a service (dropdown sourced from s3_mapping.json keys)
2) fetches recent ECR tags for that service
3) uploads a second, generated pipeline snippet containing a real dropdown of tags
4) executes rollback (currently prints the rollback image URI)

Notes:
- The tag dropdown cannot be populated from a previous step's output in a single
  static YAML file. That's why step (2) uploads a snippet.
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("Missing dependency: PyYAML") from e


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / ".buildkite" / "config" / "s3_mapping.json"


def _load_mapping_keys() -> list[str]:
    raw = MAPPING_PATH.read_text(encoding="utf-8")
    raw = "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("//")
    )
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("s3_mapping.json must be a JSON object")
    keys = sorted(str(k) for k in data.keys())
    if not keys:
        raise SystemExit("No services found in s3_mapping.json")
    return keys


def main() -> None:
    services = _load_mapping_keys()

    fetch_and_prompt_cmd = r"""set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-}"
AWS_ACCOUNT_ID="004095192903"
AWS_REGION="us-east-1"
ECR_REPOSITORY="emr_cluster"

if [ -z "${SERVICE_NAME}" ]; then
  echo "SERVICE_NAME is required" >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  if command -v apk >/dev/null 2>&1; then
    apk add --no-cache aws-cli >/dev/null
  else
    echo "aws CLI not found on agent" >&2
    exit 1
  fi
fi

TAGS="$(python3 .buildkite/list_ecr_tags.py \
  --region "${AWS_REGION}" \
  --repo "${ECR_REPOSITORY}" \
  --service "${SERVICE_NAME}" \
  --limit 30)"

if [ -z "${TAGS}" ]; then
  echo "No tags found for service ${SERVICE_NAME}" >&2
  exit 1
fi

buildkite-agent meta-data set "RB_SERVICE_NAME" "${SERVICE_NAME}"
buildkite-agent meta-data set "RB_AWS_ACCOUNT_ID" "${AWS_ACCOUNT_ID}"
buildkite-agent meta-data set "RB_AWS_REGION" "${AWS_REGION}"
buildkite-agent meta-data set "RB_ECR_REPOSITORY" "${ECR_REPOSITORY}"

{
  echo "steps:";
  echo "  - label: \"⏪ Choose Rollback Tag\"";
  echo "    key: \"rb_choose_tag\"";
  echo "    type: input";
  echo "    prompt: \"Pick the image tag to roll back to (most recent first).\"";
  echo "    fields:";
  echo "      - select: \"ROLLBACK_TAG\"";
  echo "        key: \"ROLLBACK_TAG\"";
  echo "        required: true";
  echo "        options:";

  printf '%s\n' "${TAGS}" | while IFS= read -r t; do
    [ -z "${t}" ] && continue
    esc=${t//\"/\\\"}
    printf '          - label: "%s"\n' "${esc}";
    printf '            value: "%s"\n' "${esc}";
  done

  echo "";
  echo "  - label: \"⏪ Execute rollback\"";
  echo "    key: \"rb_execute\"";
  echo "    depends_on: \"rb_choose_tag\"";
  echo "    command: |";
  echo "      set -euo pipefail";
  echo "";
  echo "      SERVICE_NAME=\"$$(buildkite-agent meta-data get RB_SERVICE_NAME)\"";
  echo "      AWS_ACCOUNT_ID=\"$$(buildkite-agent meta-data get RB_AWS_ACCOUNT_ID)\"";
  echo "      AWS_REGION=\"$$(buildkite-agent meta-data get RB_AWS_REGION)\"";
  echo "      ECR_REPOSITORY=\"$$(buildkite-agent meta-data get RB_ECR_REPOSITORY)\"";
  echo "      ROLLBACK_TAG=\"${ROLLBACK_TAG}\"";
  echo "";
  echo "      ECR_URI=\"${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com\"";
  echo "      ROLLBACK_IMAGE_URI=\"${ECR_URI}/${ECR_REPOSITORY}:${ROLLBACK_TAG}\"";
  echo "";
  echo "      echo \"Rolling back service ${SERVICE_NAME} to: ${ROLLBACK_IMAGE_URI}\"";
  echo "      echo \"TODO: add deployment logic here\"";
} | buildkite-agent pipeline upload
"""

    pipeline = {
        "steps": [
            {
                "label": "⚙️ Select Service to Roll Back",
                "key": "rb_select_service",
                "type": "input",
                "fields": [
                    {
                        "select": "SERVICE_NAME",
                        "key": "SERVICE_NAME",
                        "required": True,
                        "options": [{"label": s, "value": s} for s in services],
                    }
                ],
            },
            {
                "label": "🔎 Fetch recent ECR tags and prompt",
                "key": "rb_fetch_and_prompt",
                "depends_on": "rb_select_service",
                "command": fetch_and_prompt_cmd,
            },
        ]
    }

    print("# GENERATED FILE - DO NOT EDIT")
    print(yaml.safe_dump(pipeline, sort_keys=False))


if __name__ == "__main__":
    main()

