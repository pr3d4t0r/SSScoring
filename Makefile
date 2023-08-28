# See: https://github.com/pr3d4t0r/SSSCoring/blob/master/LICENSE.txt


SHELL=/bin/bash

BUILD=./build
DEVPI_HOST=$(shell cat devpi-hostname.txt)
DEVPI_PASSWORD=$(shell cat ./devpi-password.txt)
DEVPI_USER=$(shell cat ./devpi-user.txt)
DIST=./dist
FROZEN_PACKAGES=/tmp/requirements-frozen.txt
MANPAGES=./manpages
PACKAGE=$(shell cat package.txt)
PACKAGES_UPDATE=/tmp/packages-update.txt
REQUIREMENTS=requirements.txt
VERSION=$(shell echo "from ssscoring import __VERSION__; print(__VERSION__)" | python)


# Targets:

all: ALWAYS
	make test
	make package
	make manpage


# TODO: Use rm -Rfv $$(find $(PACKAGE) | awk '/__pycache__$$/') after the ssscoring
#       package is claimed to this project by PyPI.
clean:
	rm -Rf $(BUILD)/*
	rm -Rf $(DIST)/*
	rm -Rf $(MANPAGES)/*
	rm -Rfv $$(find ssscoring/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')
	rm -Rfv $$(find . | awk '/.ipynb_checkpoints/')
	pushd ./dist ; pip uninstall -y $(PACKAGE)==$(VERSION) || true ; popd


devpi:
	devpi use $(DEVPI_HOST)
	@devpi login $(DEVPI_USER) --password="$(DEVPI_PASSWORD)"
	devpi use $(DEVPI_USER)/dev
	devpi -v use --set-cfg $(DEVPI_USER)/dev
	@[[ -e "pip.conf-bak" ]] && rm -f "pip.conf-bak"


install:
	pip install -U $(PACKAGE)==$(VERSION)
	pip list | awk 'NR < 3 { print; } /$(PACKAGE)/'


libupdate:
	pip list --outdated | awk 'NR > 2 { print($$1); }' | tee $(PACKAGES_UPDATE)
	pip install -U pip
	pip install -Ur $(PACKAGES_UPDATE)


local:
	pip install -e .


manpage:
	mkdir -p $(MANPAGES)
	t=$$(mktemp) && awk -v "v=$(VERSION)" '/^%/ { $$4 = v; print; next; } { print; }' README.md > "$$t" && cat "$$t" > README.md && rm -f "$$t"
	pandoc --standalone --to man README.md -o $(MANPAGES)/ssscoring.1


nuke: ALWAYS
	make clean


# Reference:  https://setuptools.pypa.io/en/latest/userguide/index.html
package:
	pip install -r $(REQUIREMENTS)
	python -m build --wheel


# The publish: target is for PyPI, not for the devpi server.
# https://www.python.org/dev/peps/pep-0541/#how-to-request-a-name-transfer
#
# PyPI user name:  ciurana; pypi AT cime_net
publish:
	twine --no-color check $(DIST)/*
	twine --no-color upload --verbose $(DIST)/*


refresh: ALWAYS
	pip install -U -r requirements.txt


# Delete the Python virtual environment - necessary when updating the
# host's actual Python, e.g. upgrade from 3.7.5 to 3.7.6.
resetpy: ALWAYS
	rm -Rfv ./.Python ./bin ./build ./dist ./include ./lib


targets:
	@printf "Makefile targets:\n\n"
	@cat Makefile| awk '/:/ && !/^#/ && !/targets/ && !/Makefile/ { gsub("ALWAYS", ""); gsub(":", ""); print; } /^ALWAYS/ { next; }'


# TODO: Use rm -Rfv $$(find $(PACKAGE) | awk '/__pycache__$$/') after the ssscoring
#       package is claimed to this project by PyPI.
test: ALWAYS
	@echo "Version = $(VERSION)"
	pip install -r requirements.txt
	pip install -e .
	pytest --show-capture=no -v ./tests/*
	pip uninstall -y $(PACKAGE)==$(VERSION) || true
	rm -Rfv $$(find ssscoring/ | awk '/__pycache__$$/')
	rm -Rfv $$(find tests | awk '/__pycache__$$/')


tools:
	pip install -U devpi-client pip ptpython pudb pytest


upload:
	devpi upload dist/*whl


ALWAYS:

