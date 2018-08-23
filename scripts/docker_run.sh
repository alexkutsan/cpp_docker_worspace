#! /usr/bin/env bash
IMAGE_NAME=$1; shift

DISTCC_PORT=$1; shift
BASE_DIR=$1; shift

INTERACTION_MODE=$1; shift

EX_CONTAINER=$(docker ps | grep "$IMAGE_NAME" | awk '{print $1}')
LOCAL_CONTAINER=$(docker images | grep "$IMAGE_NAME" | grep -v sdl.docker | awk '{print $1}')

if [ ! -z "$EX_CONTAINER" ]
then
    if [ $INTERACTION_MODE = "detached" ]
    then
        echo "Container is already running"; exit 0
    fi
    docker attach $EX_CONTAINER; exit 0
fi
FULL_IMAGE_NAME=$IMAGE_NAME
if [ -z "$LOCAL_CONTAINER" ]
then
	FULL_IMAGE_NAME=sdl.docker:5000/$IMAGE_NAME
fi

[[ $INTERACTION_MODE = "detached" ]] && RUN_MODE="-d" || RUN_MODE=""

GIT_UNAME=$(git config --global user.name)
GIT_EMAIL=$(git config --global user.email)

docker run $RUN_MODE -it --rm \
  -e LOCAL_USER_ID=`id -u $USER` \
  -e DISPLAY=$DISPLAY \
  -e IMAGE_NAME=$IMAGE_NAME \
  -e GIT_AUTHOR_NAME="$GIT_UNAME" \
  -e GIT_COMMITTER_NAME="$GIT_UNAME" \
  -e GIT_AUTHOR_EMAIL="$GIT_EMAIL" \
  -e GIT_COMMITTER_EMAIL="$GIT_EMAIL" \
  --network host \
  --security-opt seccomp=unconfined \
  --privileged \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $BASE_DIR:/home/developer/pro \
  -v ~/.ssh:/home/developer/.ssh \
  $FULL_IMAGE_NAME "$@"
