from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / ".buildkite" / "config" / "s3_mapping.json"


def _load_service_names() -> list[str]:
    raw = MAPPING_PATH.read_text(encoding="utf-8")
    raw = "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("//")
    )
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("s3_mapping.json must be a JSON object")
    names = sorted(str(k) for k in data.keys())
    if not names:
        raise SystemExit("No services found in s3_mapping.json")
    return names


def _yaml_escape(s: str) -> str:
    return s.replace('"', '\\"')


def main() -> None:
    services = _load_service_names()
    default_service = services[0]

    service_options = "\n".join(
        f"          - label: \"{_yaml_escape(s)}\"\n            value: \"{_yaml_escape(s)}\""
        for s in services
    )

    yaml_text = f"""steps:
  - label: \"Select service\"
    key: \"rb_service\"
    type: input
    fields:
      - select: \"SERVICE_NAME\"
        key: \"SERVICE_NAME\"
        required: true
        default: \"{_yaml_escape(default_service)}\"
        options:
{service_options}

  - label: \"List recent image tags\"
    key: \"rb_list_tags\"
    depends_on: \"rb_service\"
    command: |
      set -euo pipefail

      SERVICE_NAME=\"${{SERVICE_NAME:-}}\"
      AWS_REGION=\"us-east-1\"
      ECR_REPOSITORY=\"emr_cluster\"
      if ! command -v aws >/dev/null 2>&1; then
        fi
      fi

      echo \"--- Recent tags for service: ${{SERVICE_NAME}} (repo: ${{ECR_REPOSITORY}}) ---\"
      python3 .buildkite/list_ecr_tags.py \\
        --region \"${{AWS_REGION}}\" \\
        --repo \"${{ECR_REPOSITORY}}\" \\
        --limit 30
"""

    print(yaml_text)


if __name__ == "__main__":
    main()
