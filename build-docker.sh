#! /bin/bash

IMAGE_NAME=robocar-tflite-steering
TAG=$(git describe)
FULL_IMAGE_NAME=docker.io/cyrilix/${IMAGE_NAME}:${TAG}

buildah bud --no-cache --platform linux/amd64 --manifest $IMAGE_NAME --rm .
#buildah bud --platform linux/arm64 --manifest $IMAGE_NAME --rm .
buildah bud --no-cache --platform linux/arm/v7 --manifest $IMAGE_NAME --rm .


# push image
printf "\n\nPush manifest to %s\n\n" "${FULL_IMAGE_NAME}"
#buildah push --all --rm -f v2s2 "localhost/$IMAGE_NAME" "docker://${FULL_IMAGE_NAME}"
podman manifest push --format v2s2 --rm "localhost/${IMAGE_NAME}" "docker://${FULL_IMAGE_NAME}"
