#!/usr/bin/env bash
IMAGE_NAME=$1

EX_CONTAINER=$(docker ps | grep "$IMAGE_NAME" | awk '{print $1}')
docker attach $EX_CONTAINER
