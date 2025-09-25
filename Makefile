# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt


SHELL=/bin/bash

API_DOC_DIR="./docs"
APP_CONFIG_FILE="config.toml"
BUILD=./build
BUILD_OS=$(shell uname)
DEVPI_HOST=$(shell cat devpi-hostname.txt)
DEVPI_PASSWORD=$(shell cat ./devpi-password.txt)
DEVPI_USER=$(shell cat ./devpi-user.txt)
DIST=./dist
FROZEN_PACKAGES=/tmp/requirements-frozen.txt
MANPAGES=./manpages
PACKAGE=$(shell cat package.txt)
PACKAGES_UPDATE=/tmp/packages-update.txt
REQUIREMENTS=requirements.txt
VERSION=$(shell echo "from $(PACKAGE) import __VERSION__; print(__VERSION__)" | python)


# Targets:

all: ALWAYS
	make test
	make package
	make manpage
	make docs
	make umountFlySight
	make DumbDriver


clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rf $(MANPAGES)/*
	rm -Rfv $$(find $(PACKAGE)/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	rm -Rfv ./.pytest_cache
	rm -Rf $(API_DOC_DIR)/*
	mkdir -p ./dist
	pushd ./dist ; pip uninstall -y $(PACKAGE)==$(VERSION) || true ; popd


devpi:
	devpi use $(DEVPI_HOST)
	@devpi login $(DEVPI_USER) --password="$(DEVPI_PASSWORD)"
	devpi use $(DEVPI_USER)/dev
	devpi -v use --set-cfg $(DEVPI_USER)/dev
	@[[ -e "pip.conf-bak" ]] && rm -f "pip.conf-bak"


dockerize.arm64: ALWAYS
	echo "$(VERSION)" > ./docker-ARM/dockerimageversion.txt
	echo "pr3d4t0r/ssscore-p" > ./docker-ARM/dockerimagename.txt
	cp $(APP_CONFIG_FILE) ./docker-ARM
	$(MAKE) -C ./docker-ARM all


dockerize: ALWAYS
	echo "$(VERSION)" > ./docker/dockerimageversion.txt
	echo "pr3d4t0r/ssscore" > ./docker/dockerimagename.txt
	cp $(APP_CONFIG_FILE) ./docker
	$(MAKE) -C ./docker all


# [[ -e ".env" ]] && mv ".env" "_env"
# [[ -e "_env" ]] && mv "_env" ".env"
docs: ALWAYS
	pip install -U pdoc
	mkdir -p $(API_DOC_DIR)
	VERSION="$(VERSION)" PDOC_ALLOW_EXEC=1 pdoc --logo="https://github.com/pr3d4t0r/SSScoring/blob/master/assets/ssscoring-logo.png?raw=true" --favicon="https://cime.net/upload_area/favicon.ico" -n -o $(API_DOC_DIR) -t ./resources $(PACKAGE)


DumbDriver: ALWAYS
	if [ "$(BUILD_OS)" = "Darwin" ]; then \
		osacompile -o $(DIST)/DumbDriver.app DumbDriver.applescript; \
		cp resources/DumbDriver.icns $(DIST)/DumbDriver.app/Contents/Resources/applet.icns; \
		ls -Al $(DIST) | grep "\.app" ; \
	fi


install:
	pip install -U $(PACKAGE)==$(VERSION)
	pip list | awk 'NR < 3 { print; } /$(PACKAGE)/'


libupdate:
	pip list --outdated | awk 'NR > 2 { print($$1); }' | tee $(PACKAGES_UPDATE)
	pip install -U pip
	pip install -Ur $(PACKAGES_UPDATE)


local:
	./tools/dzresource
	pip install -r $(REQUIREMENTS) -e .
	pip install -e .


manpage:
	mkdir -p $(MANPAGES)
	t=$$(mktemp) && awk -v "v=$(VERSION)" '/^%/ { $$4 = v; print; next; } { print; }' ssscore.md > "$$t" && cat "$$t" > ssscore.md && rm -f "$$t"
	pandoc --standalone --to man ssscore.md -o $(MANPAGES)/ssscore.1
	t=$$(mktemp) && awk -v "v=$(VERSION)" '/^%/ { $$4 = v; print; next; } { print; }' README.md > "$$t" && cat "$$t" > README.md && rm -f "$$t"
	pandoc --standalone --to man README.md -o $(MANPAGES)/$(PACKAGE).3


nuke: ALWAYS
	make clean


# Reference:  https://setuptools.pypa.io/en/latest/userguide/index.html
package:
	pip install -r $(REQUIREMENTS)
	./tools/dzresource
	python -m build --wheel


prune:
	for f in $$(git branch | awk '!/master/ && !/main/ && !/^\*/ && !/local-work/ { print; }'); do git branch -D "$$f"; done


# The publish: target is for PyPI, not for the devpi server.
# https://www.python.org/dev/peps/pep-0541/#how-to-request-a-name-transfer
#
# PyPI user name:  ciurana; pypi AT cime_net
publish:
	pip install -U twine
	twine --no-color check $(DIST)/*whl
	twine --no-color upload --verbose $(DIST)/*whl


refresh: ALWAYS
	pip install -U -r requirements.txt


# Delete the Python virtual environment - necessary when updating the
# host's actual Python, e.g. upgrade from 3.7.5 to 3.7.6.
resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


targets:
	@printf "Makefile targets:\n\n"
	@cat Makefile| awk '/:/ && !/^#/ && !/targets/ && !/Makefile/ { gsub("ALWAYS", ""); gsub(":", ""); print; } /^ALWAYS/ { next; }'


test: ALWAYS
	@echo "Version = $(VERSION)"
	cp $(APP_CONFIG_FILE) ~/.streamlit
	pytest
	rm -Rfv $$(find $(PACKAGE)/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')
	rm ~/.streamlit/$(APP_CONFIG_FILE)


tools:
	pip install -U devpi-client pip ptpython pudb pytest


umountFlySight: ALWAYS
	if [ "$(BUILD_OS)" = "Darwin" ]; then \
		osacompile -o $(DIST)/umountFlySight.app umountFlySight.applescript; \
		cp resources/FreeAgent.icns $(DIST)/umountFlySight.app/Contents/Resources/applet.icns; \
		ls -Al $(DIST) | grep "\.app" ; \
	fi


upload:
	devpi upload dist/*whl


ALWAYS:

