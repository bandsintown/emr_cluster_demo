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

    fetch_and_prompt_cmd =fetch_and_prompt_cmd = r"""set -euo pipefail

# 1. Get the service name from the FIRST input step (rb_select_service)
# In Buildkite, the key in 'fields' becomes the meta-data key.
SERVICE_NAME=$(buildkite-agent meta-data get "SERVICE_NAME")

if [ -z "$SERVICE_NAME" ]; then
  echo "Error: SERVICE_NAME meta-data is empty" >&2
  exit 1
fi

AWS_REGION="us-east-1"
ECR_REPOSITORY="emr_cluster"

# 2. Fetch tags - Ensure these variables are populated
TAGS=$(python3 .buildkite/list_ecr_tags.py \
  --region "${AWS_REGION}" \
  --repo "${ECR_REPOSITORY}" \
  --service "${SERVICE_NAME}" \
  --limit 30)

# 3. Use a simple Python one-liner to generate the next steps safely
# We export variables to the env so the python -c can pick them up easily
export SERVICE_NAME TAGS
python3 -c "
import yaml, os, sys
tags = os.environ.get('TAGS', '').splitlines()
service = os.environ.get('SERVICE_NAME')

new_pipeline = {
    'steps': [
        {
            'label': 'Choose Rollback Tag',
            'key': 'rb_choose_tag',
            'type': 'input',
            'fields': [{
                'select': 'ROLLBACK_TAG',
                'key': 'rollback_tag_selection',
                'required': True,
                'options': [{'label': t, 'value': t} for t in tags if t]
            }]
        },
        {
            'label': f'Execute rollback for {service}',
            'command': f'TAG=\\$(buildkite-agent meta-data get \"rollback_tag_selection\")\\necho \"Rolling back {service} to \\$TAG\"'
        }
    ]
}
print(yaml.dump(new_pipeline))
" | buildkite-agent pipeline upload
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
