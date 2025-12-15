# Dockerfile

# =====================================================================
# STAGE 1: Git Cloning and Asset Preparation (The Cloner/Builder Stage)
# =====================================================================
# Use a minimal image that includes the 'git' client
FROM alpine/git AS asset_cloner

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