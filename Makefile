.PHONY: docker

DOCKER_IMG = cyrilix/robocar-tflite-steering

docker:
	docker buildx build . --platform linux/arm/7,linux/arm64,linux/amd64 -t ${DOCKER_IMG} --push

