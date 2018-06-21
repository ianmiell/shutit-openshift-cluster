#!/bin/bash
set -x
set -e
# Example for running
DOCKER=${DOCKER:-docker}
IMAGE_NAME=imiell/sqlpad
CONTAINER_NAME=sqlpad
DOCKER_ARGS='-p 9010:3000'
while getopts "i:c:a:" opt
do
	case "$opt" in
	i)
		IMAGE_NAME=$OPTARG
		;;
	c)
		CONTAINER_NAME=$OPTARG
		;;
	a)
		DOCKER_ARGS=$OPTARG
		;;
	esac
done
docker rm -f sqlpad || /bin/true
${DOCKER} run -d --name ${CONTAINER_NAME} ${DOCKER_ARGS} ${IMAGE_NAME}
