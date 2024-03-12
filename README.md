# testinfra-docker
IMAGE_REVISION=$IMAGE_REVISION docker-compose run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --rm \
    "$IMAGE" \
    bash -c \
    "py.test test.py --verbose"
