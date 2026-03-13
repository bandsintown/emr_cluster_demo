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

# Install python and run the staging script to populate /app/<SERVICE_NAME>/...
RUN apk add --no-cache python3
RUN SERVICE_NAME="${SERVICE_NAME}" python3 /src/scripts/stage_service_assets.py

# Optional: keep container alive
CMD ["sleep", "infinity"]