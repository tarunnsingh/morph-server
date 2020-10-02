# Makefile for building Morph-Server
# Reference Guide - https://www.gnu.org/software/make/manual/make.html

#
# Internal variables or constants.
# NOTE - These will be executed when any make target is invoked.
#
IS_DOCKER_INSTALLED = $(shell which docker >> /dev/null 2>&1; echo $$?)

.DEFAULT_GOAL              := help
VERSION ?= latest

BASE_IMAGE_NAME ?= morph-server
BASE_CONTAINER_NAME ?= morph-server-
CONTAINER_INSTANCE ?= default

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help deps morph-server-image morph-server-start
help:				##Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

## deps:				Check if docker is installed or not
deps: _build_check_docker

_build_check_docker:
	@echo "------------------"
	@echo "--> Check the Docker deps"
	@echo "------------------"
	@if [ $(IS_DOCKER_INSTALLED) -eq 1 ]; \
		then echo "" \
		&& echo "ERROR:\tdocker is not installed. Please install it before build." \
		&& echo "" \
		&& exit 1; \
		fi;

## morph-server-build:		Builds docker Image
morph-server-build: deps
	@echo "------------------"
	@echo "--> Building Morph Server"
	@docker build -t  $(BASE_IMAGE_NAME):$(VERSION) .
	@echo "------------------"

## morph-server-start: 		start morph server api
morph-server-start:
	@echo "------------------"
	@echo "--> Morph Server Start Api"
	@ docker run -d --name $(BASE_IMAGE_NAME)-$(CONTAINER_INSTANCE) --rm -p 5000:5000 $(BASE_IMAGE_NAME)

## morph-server-stop: 		Stop morph server api
morph-server-stop:
	@ docker stop $(BASE_IMAGE_NAME)-${CONTAINER_INSTANCE}