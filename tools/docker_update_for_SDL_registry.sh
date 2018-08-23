#!/bin/bash
#Script changes docker environment to be able working with docker registry

#check an os version
version=$(lsb_release -sr)
case $version in
14.*)
    sudo echo 'DOCKER_OPTS="--insecure-registry sdl.docker:5000"' | sudo tee -a /etc/default/docker
    ;;
*)
    sudo sed -i -e 's/^ExecStart.*/ExecStart=\/usr\/bin\/dockerd -H fd:\/\/ --insecure-registry sdl.docker:5000/g' /lib/systemd/system/docker.service
    sudo systemctl daemon-reload
esac

#define registry ip address
sudo echo '172.30.23.4 sdl.docker' | sudo tee -a /etc/hosts

#restart docker service to apply changes
sudo service docker restart