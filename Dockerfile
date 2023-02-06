FROM tensorflow/tensorflow:1.13.2-gpu-py3

ARG USERNAME=nbg
ARG UID=1000
ARG GID=1000

# Change repository for faster downloads (South Korea)
RUN sed -i 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list

# # Fix GPG key error
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/3bf863cc.pub
RUN apt update -y && apt install apt-transport-https wget

# Install OpenEXR
RUN apt update && apt install -y openexr libopenexr-dev

# Upgrade pip
RUN pip install --upgrade pip

# Install required python packages
RUN pip install scipy scikit-image Pillow openexr

# Add non-root user
RUN groupadd -g $GID -o $USERNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $USERNAME
USER $USERNAME

WORKDIR /nbg