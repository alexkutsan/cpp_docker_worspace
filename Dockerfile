FROM ubuntu:20.04

ENV TZ=Europe/Minsk
ENV DEBIAN_FRONTEND noninteractive

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /home/developer/pro

RUN apt update && apt install -yq \
    sudo \
    cowsay \
    git \
    git-gui \
    tmux \
    wget \
    zsh \
    vim \
    fonts-powerline \
    gitk \
    meld \
    tree \
    locales \
    gnupg

# Setup locale
RUN locale-gen en_US.UTF-8

# ZSH config
RUN git clone https://github.com/robbyrussell/oh-my-zsh /opt/oh-my-zsh && \
    cp /opt/oh-my-zsh/templates/zshrc.zsh-template .zshrc && \
    cp -r /opt/oh-my-zsh .oh-my-zsh && \
    cp /opt/oh-my-zsh/templates/zshrc.zsh-template /home/developer/.zshrc && \
    cp -r /opt/oh-my-zsh /home/developer/.oh-my-zsh && \
    sed  "s/robbyrussell/bira/" -i /home/developer/.zshrc && \
    echo "PROMPT=\$(echo \$PROMPT | sed 's/%m/%f\$IMAGE_NAME/g')" >> /home/developer/.zshrc && \
    echo "RPROMPT=''" >> /home/developer/.zshrc

# Tmux config
WORKDIR /opt
RUN git clone https://github.com/gpakosz/.tmux.git && \
    echo "set-option -g default-shell /bin/zsh" >> .tmux/.tmux.conf
COPY onStartup/tmux_setup.sh /opt/startup/

# Sublime instalation
ARG SUBLIME_BUILD="${SUBLIME_BUILD:-3207}"
RUN wget --no-check-certificate  https://download.sublimetext.com/sublime-text_build-"${SUBLIME_BUILD}"_amd64.deb --no-check-certificate && \
    dpkg -i sublime-text_build-"${SUBLIME_BUILD}"_amd64.deb

# SSH setup

COPY onStartup/ssh_setup.sh /opt/startup/

# Build
RUN apt update && apt install -yq \
    cmake \
    cmake-curses-gui \
    ccache \
    g++ \
    gdb \
    clang \
    clang-format 

# Build
RUN apt update && apt install -yq \
    qtcreator

COPY onStartup/entrypoint.sh /usr/bin/
WORKDIR /home/developer
ENTRYPOINT ["/bin/bash", "-e", "/usr/bin/entrypoint.sh"]
CMD ["/bin/zsh"]
