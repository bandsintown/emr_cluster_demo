# Dockerfile

# =====================================================================
# STAGE 1: Git Cloning and Asset Preparation (The Cloner/Builder Stage)
# =====================================================================
# Use a minimal image that includes the 'git' client
FROM alpine/git AS asset_cloner

# 1. Define Build Arguments for GitHub source and versioning
ARG GITHUB_REPO="https://github.com/your-org/your-repo.git"
ARG GITHUB_COMMIT="main" # Or a specific commit hash/tag
ARG SOURCE_SUBDIR="my-service/static-assets"

# Pass the Buildkite commit hash (or any unique ID) for versioning
ARG BUILD_VERSION

# Set the working directory
WORKDIR /tmp/repo

# 2. Clone the repository
RUN git clone --depth 1 --branch ${GITHUB_COMMIT} ${GITHUB_REPO} .

# 3. Move the desired subdirectory to a final, accessible location
WORKDIR /assets
# NOTE: Using 'mv' here is fine, but if you need to copy specific files/dirs, adjust this.
RUN mv /tmp/repo/${SOURCE_SUBDIR}/ static_content/

# 4. Create the VERSION_HASH.txt file and put it inside the content directory
RUN echo "$BUILD_VERSION" > static_content/VERSION_HASH.txt


# =====================================================================
# STAGE 2: Final Image (Just an Asset Container)
# =====================================================================
# Use a minimal Alpine base image, which is tiny but still has a shell
# for running the container in the background to allow 'docker cp'.
FROM alpine:latest AS final_asset_image

# 1. Set the final image's working directory
WORKDIR /app

# 2. Copy the final assets and the version file from the cloner stage
# We copy the 'static_content' directory into the final image's /app/assets path.
COPY --from=asset_cloner /assets/static_content ./assets

# You can set a simple entrypoint, but it's not strictly necessary if
# the image is only used for extraction via 'docker create' and 'docker cp'.
# ENTRYPOINT ["/bin/sh"]