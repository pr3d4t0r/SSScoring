# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
FROM                --platform=linux/amd64 python:3.10-slim-bookworm
MAINTAINER          sopel_ai AT cime.net


RUN                 useradd -b /home/sopel_ai -m -d /home/sopel_ai -s /bin/bash sopel_ai
RUN                 pip install -U pip \
                        sopel \
                        sopel_ai

COPY                ./runsopel /usr/local/bin/runsopel
USER                sopel_ai
WORKDIR             /home/sopel_ai
# TODO:
# https://sopel.chat/docs/cli.html#supported-environment-variables
CMD                 /usr/local/bin/runsopel

