from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / ".buildkite" / "config" / "s3_mapping.json"


def _load_service_names() -> list[str]:
    raw = MAPPING_PATH.read_text(encoding="utf-8")
    raw = "\n".join(line for line in raw.splitlines() if not line.lstrip().startswith("//"))
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("s3_mapping.json must be a JSON object")
    names = sorted(str(k) for k in data.keys())
    if not names:
        raise SystemExit("No services found in s3_mapping.json")
    return names


def _yaml_quote(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def _emit(obj, indent: int = 0) -> None:
    sp = "  " * indent

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                print(f"{sp}{k}:")
                _emit(v, indent + 1)
            else:
                if isinstance(v, str):
                    print(f"{sp}{k}: {_yaml_quote(v)}")
                elif v is True:
                    print(f"{sp}{k}: true")
                elif v is False:
                    print(f"{sp}{k}: false")
                elif v is None:
                    print(f"{sp}{k}: null")
                else:
                    print(f"{sp}{k}: {v}")
        return

    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                print(f"{sp}-")
                _emit(item, indent + 1)
            else:
                if isinstance(item, str):
                    print(f"{sp}- {_yaml_quote(item)}")
                else:
                    print(f"{sp}- {item}")
        return

    raise TypeError(f"Unsupported type: {type(obj)}")


def main() -> None:
    services = _load_service_names()

    persist_service_cmd = """set -euo pipefail
if [ -z \"${SERVICE_NAME:-}\" ]; then
  echo \"SERVICE_NAME is required\" >&2
  exit 1
fi
buildkite-agent meta-data set RB_SERVICE_NAME \"${SERVICE_NAME}\"\n"""

    fetch_and_prompt_cmd = """set -euo pipefail

SERVICE_NAME=\"$$(buildkite-agent meta-data get RB_SERVICE_NAME)\"
AWS_ACCOUNT_ID=\"004095192903\"
AWS_REGION=\"us-east-1\"
ECR_REPOSITORY=\"emr_cluster\"\n
if [ -z \"${SERVICE_NAME}\" ]; then
  echo \"RB_SERVICE_NAME is required\" >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  if command -v apk >/dev/null 2>&1; then
    apk add --no-cache aws-cli >/dev/null
  else
    echo \"aws CLI not found on agent\" >&2
    exit 1
  fi
fi

TAGS=\"$$(python3 .buildkite/list_ecr_tags.py \\
  --region \"${AWS_REGION}\" \\
  --repo \"${ECR_REPOSITORY}\" \\
  --service \"${SERVICE_NAME}\" \\
  --limit 30)\"\n
if [ -z \"${TAGS}\" ]; then
  echo \"No tags found for service ${SERVICE_NAME}\" >&2
  exit 1
fi

buildkite-agent meta-data set RB_AWS_ACCOUNT_ID \"${AWS_ACCOUNT_ID}\"
buildkite-agent meta-data set RB_AWS_REGION \"${AWS_REGION}\"
buildkite-agent meta-data set RB_ECR_REPOSITORY \"${ECR_REPOSITORY}\"\n
{
  echo \"steps:\";
  echo \"  - label: \\\"Choose Rollback Tag\\\"\";
  echo \"    key: \\\"rb_choose_tag\\\"\";
  echo \"    type: input\";
  echo \"    prompt: \\\"Pick the image tag to roll back to (most recent first).\\\"\";
  echo \"    fields:\";
  echo \"      - select: \\\"ROLLBACK_TAG\\\"\";
  echo \"        key: \\\"ROLLBACK_TAG\\\"\";
  echo \"        required: true\";
  echo \"        options:\";

  printf '%s\\n' \"${TAGS}\" | while IFS= read -r t; do
    [ -z \"${t}\" ] && continue
    esc=\"${t//\\\"/\\\\\\\"}\"
    printf '          - label: \"%s\"\\n' \"${esc}\"
    printf '            value: \"%s\"\\n' \"${esc}\"
  done

  echo \"\";
  echo \"  - label: \\\"Execute rollback\\\"\";
  echo \"    key: \\\"rb_execute\\\"\";
  echo \"    depends_on: \\\"rb_choose_tag\\\"\";
  echo \"    command: |\";
  echo \"      set -euo pipefail\";
  echo \"\";
  echo \"      SERVICE_NAME=\\\"$$(buildkite-agent meta-data get RB_SERVICE_NAME)\\\"\";
  echo \"      AWS_ACCOUNT_ID=\\\"$$(buildkite-agent meta-data get RB_AWS_ACCOUNT_ID)\\\"\";
  echo \"      AWS_REGION=\\\"$$(buildkite-agent meta-data get RB_AWS_REGION)\\\"\";
  echo \"      ECR_REPOSITORY=\\\"$$(buildkite-agent meta-data get RB_ECR_REPOSITORY)\\\"\";
  echo \"      ROLLBACK_TAG=\\\"${ROLLBACK_TAG}\\\"\";
  echo \"\";
  echo \"      ECR_URI=\\\"${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com\\\"\";
  echo \"      ROLLBACK_IMAGE_URI=\\\"${ECR_URI}/${ECR_REPOSITORY}:${ROLLBACK_TAG}\\\"\";
  echo \"\";
  echo \"      echo \\\"Rolling back service ${SERVICE_NAME} to: ${ROLLBACK_IMAGE_URI}\\\"\";
} | buildkite-agent pipeline upload\n"""

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

    _emit(pipeline)


if __name__ == "__main__":
    main()
