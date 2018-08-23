# SDL workspace (as it supposed to be)

## Desciption :

Workspace for basic C++ development

## Dependencies:

 - make
 - docker

## Prerequirements:

## Usage:


### Easy run:

0. `$ make`
1. `$ make run`
2. ...
3. Profit! (you should be inside the container now)

This command will run docker image and run `zsh` terminal in it.

<b>Note:</b> Current guide describes work with `cpp_workspace` docker container.

#### Keep in mind:

* There is no need to quit from the container. It can be run on a background (`Ctrl+p, Ctrl+q` to detach). Moreover, if the container is not running, other developers can't use your host for a build.
* All environment settings will be reset once you've quit the container. Data in mounted volumes is on your local machine, so nothing from `/home/developer/pro/` will be lost.

#### Notes:

* Feel free to use the container as an additional terminal.
* GUI applications can be ran as well (`sublime` is preinstalled).
* On the first run, the image will be taken from private SDL registry, so it takes a while.
* If container works on background, `make run` command will attach to it.
* Username inside the container is `developer` however it replicates local UID to avoid access issues in mounted volumes.
* Local `~/pro` directory will be mounted to `/home/developer/pro` inside docker container.
* SSH keys will be replicated from host user settings.
* If you've detached from the container and try 'make run' again, you will be reattached to the container instead of restarting one.
* `tmux` and `oh-my-zsh` already set up (you're welcome)

## Advanced usage:

### Make commands description:

```
$ make
```
 * build custom docekr image with black jack

```
$ make run
```
 * Run container.
   * The Image will be downloaded if there is no any.
   * The manually built image has higher priority.

```
$ make update
```
 * Update docker image from remote registry.

```
$ make clean
```
 * Removes unused docker data:
    * All stopped containers;
    * All networks not used by at least one container;
    * All dangling images;
    * All build cache.

### Manual run :

```
docker run -it --rm  \
           -e LOCAL_USER_ID=`id -u $USER`
           -e DISPLAY=$DISPLAY \
           -e IMAGE_NAME=sdl_developer \
           -p 3632:3632 \
           --security-opt seccomp=unconfined \
           --privileged \
           -v /tmp/.X11-unix:/tmp/.X11-unix \
           -v ~/pro:/home/developer/pro \
           -v ~/.ssh:/home/developer/.ssh \
           cpp_developer
```
* LOCAL_USER_ID - is for replication of your user id to avoid permission issues
* DISPLAY - allows you to use gui applications inside container (`-v /tmp/.X11-unix:/tmp/.X11-unix` also required)
* IMAGE_NAME - used as image name inside container for self identification
* -p `port`:3632 - mapping container port to local port (used for distcc). Feel free to use alternative port of host but keep in mind that host list to be used for build on other machines should be changed according to your changes to use your machine
* -v `sdl_directory`:/home/developer/sdl - base SDL directory (`~/sdl/` by default)
* -v `ssh_keys_directory`:/home/developer/.ssh - mapping ssh keys to docekr container
* `cpp_developer` - image name to be run

Note: With option `-v` you can mount local directories inside docker containter.

