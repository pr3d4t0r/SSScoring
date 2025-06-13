# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

ARG                 PLATFORM="linux/amd64"
FROM                --platform=$PLATFORM python:latest
LABEL               maintainer="ssscoring AT cime.net"
ARG                 SERVICE_ACCOUNT="ssscore"
ARG                 VERSION="0.0.0"
ARG                 APP_CONFIG_DIR="/home/$SERVICE_ACCOUNT/.streamlit"


USER            root

RUN             DEBIAN_FRONTEND=noninteractive && \
                apt-get update && \
                apt-get -y upgrade && \
                apt-get -y --no-install-recommends install \
                    bsdmainutils \
                    ca-certificates \
                    curl \
                    git \
                    tree \
                    vim \
                    && apt-get autoremove && apt-get clean && rm -Rf /var/lib/apt/lists/*
RUN                 useradd -b /home/$SERVICE_ACCOUNT -m -d /home/$SERVICE_ACCOUNT -s /bin/bash $SERVICE_ACCOUNT
RUN                 pip install -U pip \
                        ssscoring==$VERSION

WORKDIR         /home/$SERVICE_ACCOUNT
RUN             mkdir $APP_CONFIG_DIR
COPY            app.py /home/$SERVICE_ACCOUNT
COPY            config.toml $APP_CONFIG_DIR
RUN             chown $SERVICE_ACCOUNT:$SERVICE_ACCOUNT app.py
RUN             chown -Rfv $SERVICE_ACCOUNT:$SERVICE_ACCOUNT $APP_CONFIG_DIR


USER            $SERVICE_ACCOUNT
HEALTHCHECK     CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT      [ "streamlit", "run", "/home/ssscore/app.py", "--server.address=0.0.0.0" ]

