#!/bin/bash

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

USER_ID=${LOCAL_USER_ID:-9001}

useradd --shell /bin/bash -u $USER_ID -o -c "" developer
echo "developer ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

chown developer /home/developer
chgrp developer /home/developer

export HOME=/home/developer

echo "export LANG=en_US.UTF-8" >> /home/developer/.zshrc

[ -e /opt/startup/ ] && for script in /opt/startup/*; do bash $script ; done

printf "Starting with user developer, UID : $USER_ID \n\n"
echo   "    You may run sudo without password"
printf "    You may run GIU applications in container\n\n"
/usr/games/cowsay -f koala "Welcome to $IMAGE_NAME!"
sudo -E -u developer "$@"