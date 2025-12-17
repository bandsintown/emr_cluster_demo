#!/usr/bin/env python3
"""
Push changed files from a GitHub commit to correct S3 bucket based on provided "environment".
"""
import os
import sys
import argparse
import boto3


class GitHubS3Uploader:
    """
    Upload changed files from GitHub to S3 bucket based on environment.
    """
    def __init__(self, env="prod"):
        session = boto3.Session(profile_name="bit-prod")
        s3_resource = session.resource('s3')

        if env == "prod":
            bucket_name = "bit-emr-cluster"
        elif env == "dev":
            bucket_name = "bit-emr-cluster-dev"
        else:
            sys.exit(f"Unknown environment: {env}")

        print(f"\n--- Uploading files to s3://{bucket_name}")
        self.bucket = s3_resource.Bucket(bucket_name)  # type: ignore
    
    def upload_files(self, local_dir):
        """Upload the specified files to S3."""
        files_for_export = []
        for root, dirs, files in os.walk(local_dir):
            # Skip system dirs that cause errors
            skip_dirs = ["/proc", "/sys", "/dev", "/tmp", "/run", "/var/run"]
            if any(root.startswith(d) for d in skip_dirs):
                continue

            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                files_for_export.append(relative_path)
                
        for local_file in files_for_export:
            # Check that the file exists
            if os.path.exists(local_file):
                print(f"  Uploading: {local_file}")
                # self.bucket.upload_file(
                #     Filename=local_file,
                #     Key=local_file
                # )


def main():
    parser = argparse.ArgumentParser(description="Push changed files from GitHub to S3 bucket")
    parser.add_argument("--environment", "--env", choices=["prod", "dev"], default="prod", help="Target environment (prod or dev)")
    parser.add_argument("--root", default="/", help="Root directory to start copying from")
    parser.add_argument("--image-tag", help="service_name")
    
    args = parser.parse_args()
    
    print(f"=== S3 Upload Configuration ===")
    print(f"Environment: {args.environment.upper()}")
    print(f"================================\n")

    uploader = GitHubS3Uploader(env=args.environment)
    
    # Upload files
    uploader.upload_files(local_dir=".")


if __name__ == "__main__":
    main()