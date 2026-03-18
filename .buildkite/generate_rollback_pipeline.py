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

    # 1. Get the selections
    SERVICE_NAME=$(buildkite-agent meta-data get "SERVICE_NAME")
    AWS_REGION="us-east-1"
    ECR_REPOSITORY="emr_cluster"

    # 2. Get the tags from your existing script
    TAGS=$(python3 .buildkite/list_ecr_tags.py --region "${AWS_REGION}" --repo "${ECR_REPOSITORY}" --service "${SERVICE_NAME}" --limit 30)

    if [ -z "${TAGS}" ]; then
      echo "No tags found for ${SERVICE_NAME}" >&2
      exit 1
    fi

    # 3. Use Python to generate the YAML safely. 
    # This avoids all quoting/escaping/indentation issues in Bash.
    python3 -c "
    import yaml, sys

    tags = sys.stdin.read().splitlines()
    service = '${SERVICE_NAME}'

    pipeline = {
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
                'command': 'TAG=\$(buildkite-agent meta-data get \"rollback_tag_selection\")\necho \"Rolling back to \$TAG\"'
            }
        ]
    }
    print(yaml.dump(pipeline))
    " <<< "${TAGS}" | buildkite-agent pipeline upload
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
