# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
DOCKER_IMAGE_NAME_FILE=dockerimagename.txt
DOCKER_IMAGE_VERSION_FILE=dockerimageversion.txt
DOCKER_IMAGE=$(shell cat $(DOCKER_IMAGE_NAME_FILE))
DOCKER_VERSION=$(shell cat $(DOCKER_IMAGE_VERSION_FILE))
README_TMP="/tmp/README.md"

include ./build.mk


all:
	make version
	pushd arm64 && make image && make push && popd
	make image && make push


clean:
	docker image rm -f $$(docker image ls | awk '/none/ { print($$3); }')


prune:
	for f in $$(git branch | awk '!/master/ && !/main/ && !/^\*/ && !/local-work/ { print; }'); do git branch -D "$$f"; done


version:
	cp "$(DOCKER_IMAGE_VERSION_FILE)" arm64
	awk -v "version=${DOCKER_VERSION}" \
		'/^# Lucyfer/ && NR < 3 { printf("# Lucyfer %s\n", version); next; } { print; }' README.md \
		> ${README_TMP} \
		&& cp ${README_TMP} README.md

