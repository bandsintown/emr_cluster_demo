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
    raw = "\n".join(line for line in raw.splitlines() if not line.lstrip().startswith("//"))
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("s3_mapping.json must be a JSON object")
    keys = sorted(str(k) for k in data.keys())
    if not keys:
        raise SystemExit("No services found in s3_mapping.json")
    return keys


def main() -> None:
    services = _load_mapping_keys()

    persist_service_cmd = r"""set -euo pipefail
if [ -z \"${SERVICE_NAME:-}\" ]; then
  echo \"SERVICE_NAME is required\" >&2
  exit 1
fi
buildkite-agent meta-data set RB_SERVICE_NAME \"${SERVICE_NAME}\"\n"""

    fetch_and_prompt_cmd = r"""set -euo pipefail

# 1. Retrieve SERVICE_NAME exactly like your working build script
SERVICE_NAME=$$(buildkite-agent meta-data get 'SERVICE_NAME')

if [ -z "${SERVICE_NAME}" ]; then
  echo "Error: SERVICE_NAME is required" >&2
  exit 1
fi

AWS_REGION="us-east-1"
ECR_REPOSITORY="emr_cluster"

# 2. Fetch tags (using the variable we just got)
TAGS=$(python3 .buildkite/list_ecr_tags.py \
  --region "${AWS_REGION}" \
  --repo "${ECR_REPOSITORY}" \
  --service "${SERVICE_NAME}" \
  --limit 30)

if [ -z "${TAGS}" ]; then
  echo "No tags found for service ${SERVICE_NAME}" >&2
  exit 1
fi

# 3. Generate the Rollback UI safely
# We use a heredoc with 'EOF' in quotes to prevent early shell expansion
cat <<'EOF' | buildkite-agent pipeline upload
steps:
  - label: "⏪ Choose Rollback Tag"
    key: "rb_choose_tag"
    type: input
    fields:
      - select: "ROLLBACK_TAG"
        key: "rollback_tag_selection"
        required: true
        options:
$(echo "${TAGS}" | awk '{ print "          - label: \"" $0 "\"\n            value: \"" $0 "\"" }')

  - label: "🚀 Execute Rollback"
    depends_on: "rb_choose_tag"
    command: |
      set -euo pipefail
      # Retrieve the tag selected in the step above
      TAG=$$(buildkite-agent meta-data get "rollback_tag_selection")
      SERVICE=$$(buildkite-agent meta-data get "SERVICE_NAME")
      
      echo "Rolling back ${SERVICE} to tag: ${TAG}"
      # Logic for deployment goes here
EOF
"""

    pipeline = {
        "steps": [
            {
                "label": "Select Service to Roll Back",
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
                "label": "Persist service selection",
                "key": "rb_persist_service",
                "depends_on": "rb_select_service",
                "command": persist_service_cmd,
            },
            {
                "label": "Fetch recent ECR tags",
                "key": "rb_fetch_and_prompt",
                "depends_on": "rb_persist_service",
                "command": fetch_and_prompt_cmd,
            },
        ]
    }

    # Only YAML on stdout
    print(yaml.safe_dump(pipeline, sort_keys=False, allow_unicode=False))


if __name__ == "__main__":
    main()
