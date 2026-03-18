from __future__ import annotations


def main() -> None:
    # SERVICE_NAME is expected to come from a previous pipeline step.
    # No interactive selection of service or tag.
    print(
        """steps:
  - label: "Rollback: push previous tag to S3"
    key: "rb_prev_tag_and_s3"
    command: |
      set -euo pipefail

      SERVICE_NAME="$$(buildkite-agent meta-data get SERVICE_NAME)"
      AWS_REGION="us-east-1"
      ECR_REPOSITORY="emr_cluster"

      if [ -z "${SERVICE_NAME}" ]; then
        echo "SERVICE_NAME meta-data is required" >&2
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

      TAGS=$(python3 .buildkite/list_ecr_tags.py \
        --region "${AWS_REGION}" \
        --repo "${ECR_REPOSITORY}" \
        --service "${SERVICE_NAME}" \
        --limit 10)

      PREV_TAG=$(printf '%s\n' "${TAGS}" | sed -n '2p')
      if [ -z "${PREV_TAG}" ]; then
        echo "Not enough tags found for service ${SERVICE_NAME} to choose previous tag" >&2
        exit 1
      fi

      echo "Using previous tag: ${PREV_TAG}"

      # s3-push.yml reads BUILD_TAG to set IMAGE_TAG in the uploader container
      buildkite-agent meta-data set BUILD_TAG "${PREV_TAG}"

      buildkite-agent pipeline upload .buildkite/s3-push.yml
"""
    )


if __name__ == "__main__":
    main()
