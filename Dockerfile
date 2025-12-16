# Dockerfile

# =====================================================================
# STAGE 1: Git Cloning and Asset Preparation (The Cloner/Builder Stage)
# =====================================================================
# Use a minimal image that includes the 'git' client
FROM alpine:latest

# Accept service name as build argument
ARG SERVICE_NAME

WORKDIR /app

# Copy the folder specified by SERVICE_NAME into the image
COPY ${SERVICE_NAME}/ ./

# Optional: keep container alive
CMD ["sleep", "infinity"]