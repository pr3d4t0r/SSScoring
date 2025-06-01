# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
ARG                 PLATFORM="linux/amd64"
FROM                --platform=$PLATFORM python:latest
LABEL               maintainer="ssscoring AT cime.net"


USER            root

RUN             DEBIAN_FRONTEND=noninteractive && \
                apt-get update && \
                apt-get -y upgrade && \
                apt-get -y --no-install-recommends install \
                    bat \
                    bsdmainutils \
                    ca-certificates \
                    curl \
                    git \
                    gnupg \
                    jq \
                    ssh \
                    tree \
                    vim \
                    && apt-get autoremove && apt-get clean && rm -Rf /var/lib/apt/lists/*
RUN                 useradd -b /home/sopel_ai -m -d /home/sopel_ai -s /bin/bash sopel_ai
RUN                 pip install -U pip \
                        sopel \
                        sopel_ai


