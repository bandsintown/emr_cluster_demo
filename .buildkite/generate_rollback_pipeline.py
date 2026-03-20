from __future__ import annotations


def main() -> None:
    fetch_and_prompt_cmd = r"""set -euo pipefail

# 1. Get Service Name from meta-data (set by the build pipeline)
SERVICE_NAME="DailyArtistMetrics"
AWS_REGION="us-east-1"
ECR_REPOSITORY="emr_cluster"

if [ -z "$${SERVICE_NAME}" ]; then
  echo "Error: SERVICE_NAME meta-data is required" >&2
  exit 1
fi

echo "--- Fetching tags for $${SERVICE_NAME}..."

# 2. Get the 2 most recent tags (0 = current, 1 = previous)
# list_ecr_tags.py outputs tags one per line, newest first
TAGS_RAW="$(python3 .buildkite/list_ecr_tags.py \
  --region "$${AWS_REGION}" \
  --repo "$${ECR_REPOSITORY}" \
  --service "$${SERVICE_NAME}" \
  --limit 2)"
# ADD THESE LINES TO DEBUG
echo "Tags found:"
if [ -z "${TAGS_RAW}" ]; then
  echo "(None)"
  echo "Error: Could not find any tags for ${SERVICE_NAME} in ${ECR_REPOSITORY}." >&2
  exit 1
else
  echo "${TAGS_RAW}"
fi

# CURRENT_TAG="$(printf '%s\n' "${TAGS_RAW}" | sed -n '1p')"
# PREVIOUS_TAG="$(printf '%s\n' "${TAGS_RAW}" | sed -n '2p')"
# 
# if [ -z "${PREVIOUS_TAG}" ]; then
#   echo "Error: Could not find a previous tag to roll back to!" >&2
#   exit 1
# fi

# echo "--- Recent tags for ${SERVICE_NAME} (repo=${ECR_REPOSITORY}, region=${AWS_REGION}) ---"
# python3 .buildkite/list_ecr_tags.py \
#   --region "${AWS_REGION}" \
#   --repo "${ECR_REPOSITORY}" \
#   --service "${SERVICE_NAME}" \
#   --limit 30
"""

    print(
        """steps:
  - label: "Rollback: list tags"
    key: "rb_list_tags"
    command: |
"""
        + "\n".join(f"      {line}" for line in fetch_and_prompt_cmd.rstrip("\n").splitlines())
        + "\n"
    )


if __name__ == "__main__":
    main()
