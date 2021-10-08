#! /bin/bash

IMAGE_NAME=robocar-tflite-steering
TAG=$(git describe)
FULL_IMAGE_NAME=docker.io/cyrilix/${IMAGE_NAME}:${TAG}


podman build --platform linux/amd64 --manifest $IMAGE_NAME --rm .
#buildah bud --platform linux/arm64 --manifest $IMAGE_NAME --rm .
podman build --platform linux/arm/v7 --manifest $IMAGE_NAME --rm .


# push image
printf "\n\nPush manifest to %s\n\n" ${FULL_IMAGE_NAME}
podman manifest push --rm -f v2s2 "localhost/$IMAGE_NAME" "docker://${FULL_IMAGE_NAME}" --all