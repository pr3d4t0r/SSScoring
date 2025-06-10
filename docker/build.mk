# License:  https://raw.githubusercontent.com/pr3d4t0r/lucyfer/master/LICENSE.txt

image:
	docker build --progress=plain --compress --force-rm --build-arg VERSION=$(DOCKER_VERSION) -t $(DOCKER_IMAGE):$(DOCKER_VERSION) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_VERSION) $(DOCKER_IMAGE):latest


push:
	docker push $(DOCKER_IMAGE):$(DOCKER_VERSION)
	docker push $(DOCKER_IMAGE):latest

