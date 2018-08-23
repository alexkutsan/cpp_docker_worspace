#!/bin/bash

#install distcc and distccmon-gnome (monitor for distcc)
apt install distcc distccmon-gnome

#create .distcc directory in home directory if needed
[ -d $HOME/.distcc ] || mkdir -p $HOME/.distcc

REALPATH=$(realpath "$0")
DIRNAME=$(dirname $REALPATH)
HOSTS_FILE=$DIRNAME/hosts

#copy list of potential slaves to .distcc directory
cp $HOSTS_FILE $HOME/.distcc/