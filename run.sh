#/bin/bash

# Remove previous image
docker rmi nbg

# Build docker image
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) . -t nbg

# Launch a container
docker run --gpus all -dit -v `pwd`:/nbg nbg