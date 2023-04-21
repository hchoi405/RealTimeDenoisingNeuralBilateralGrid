#/bin/bash

# Remove previous image
docker rmi nbg

# Build docker image
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) . -t nbg

# Launch a container
docker run --gpus all -dit -v `pwd`:/nbg -v /media/hchoi/extra:/dataset_falcor -v /home/hchoi/nas:/nas nbg