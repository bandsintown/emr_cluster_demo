# Dockerfile

# =====================================================================
# STAGE 1: Git Cloning and Asset Preparation (The Cloner/Builder Stage)
# =====================================================================
# Use a minimal image that includes the 'git' client
FROM alpine:latest

# Accept service name as build argument
ARG SERVICE_NAME

WORKDIR /app

# Copy repository context into the image so we can pick mapped paths dynamically
COPY . /src

# Copy only the mapped files/dirs for SERVICE_NAME into /app/${SERVICE_NAME}/, preserving structure
RUN set -euo pipefail; \
    apk add --no-cache python3; \
    python3 - <<'PY'
import json
import os
import shutil
from pathlib import Path

service = os.environ.get('SERVICE_NAME')
if not service:
    raise SystemExit('SERVICE_NAME build-arg is required')

mapping_path = Path('/src/.buildkite/config/s3_mapping.json')
raw_lines = []
for line in mapping_path.read_text(encoding='utf-8').splitlines():
    if line.lstrip().startswith('//'):
        continue
    raw_lines.append(line)

data = json.loads('\n'.join(raw_lines))
paths = data.get(service)
if not isinstance(paths, list):
    raise SystemExit(f'No mapping found for service: {service}')

src_root = Path('/src')
out_root = Path('/app') / service
out_root.mkdir(parents=True, exist_ok=True)

for p in paths:
    rel = str(p).lstrip('/')
    if rel.endswith('/'):
        base = src_root / rel.rstrip('/')
        if not base.exists():
            continue
        for f in base.rglob('*'):
            if f.is_dir():
                continue
            dest = out_root / f.relative_to(src_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(f), str(dest))
    else:
        f = src_root / rel
        if not f.is_file():
            continue
        dest = out_root / f.relative_to(src_root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(f), str(dest))
PY

# Optional: keep container alive
CMD ["sleep", "infinity"]