# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
DOCKER_IMAGE_NAME_FILE=dockerimagename.txt
DOCKER_IMAGE_VERSION_FILE=dockerimageversion.txt
DOCKER_IMAGE=$(shell cat $(DOCKER_IMAGE_NAME_FILE))
DOCKER_VERSION=$(shell cat $(DOCKER_IMAGE_VERSION_FILE))
README_TMP="/tmp/README.md"

include ./build.mk


all:
	make image && make push


clean:
	docker image rm -f $$(docker image ls | awk '/none/ { print($$3); }')

