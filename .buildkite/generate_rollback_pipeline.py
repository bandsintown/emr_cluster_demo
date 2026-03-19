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
  --region "${AWS_REGION}" \
  --repo "${ECR_REPOSITORY}" \
  --service "$${SERVICE_NAME}" \
  --limit 2)"

CURRENT_TAG="$(printf '%s\n' "${TAGS_RAW}" | sed -n '1p')"
PREVIOUS_TAG="$(printf '%s\n' "${TAGS_RAW}" | sed -n '2p')"

if [ -z "${PREVIOUS_TAG}" ]; then
  echo "Error: Could not find a previous tag to roll back to!" >&2
  exit 1
fi

# Persist for the execute step
buildkite-agent meta-data set "CURRENT_TAG" "${CURRENT_TAG}"
buildkite-agent meta-data set "PREVIOUS_TAG" "${PREVIOUS_TAG}"

# 3. Upload the confirmation and execution steps
cat <<EOF | buildkite-agent pipeline upload
steps:
  - block: "Confirm Rollback for ${SERVICE_NAME}"
    prompt: "Currently deployed: ${CURRENT_TAG}\nRoll back to: ${PREVIOUS_TAG}?"
    key: "confirm_rollback"

  - label: "Executing Rollback"
    depends_on: "confirm_rollback"
    command: |
      set -euo pipefail

      SERVICE_NAME="$$(buildkite-agent meta-data get SERVICE_NAME)"
      PREVIOUS_TAG="$$(buildkite-agent meta-data get PREVIOUS_TAG)"

      echo "--- Deploying Previous Tag ---"
      echo "Service: ${SERVICE_NAME}"
      echo "Target Tag: ${PREVIOUS_TAG}"

      # TODO: add deployment logic here
      echo "Successfully initiated rollback to ${PREVIOUS_TAG}"
EOF
"""

    # Minimal rollback pipeline: single step that fetches tags and uploads confirm+execute.
    print(
        """steps:
  - label: "Rollback: fetch previous tag and confirm"
    key: "rb_fetch_and_confirm"
    command: |
"""
        + "\n".join(f"      {line}" for line in fetch_and_prompt_cmd.rstrip("\n").splitlines())
        + "\n"
    )


if __name__ == "__main__":
    main()
